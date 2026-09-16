from __future__ import annotations

import re
import unicodedata

import cv2
import numpy as np
import pytesseract

from .catalog import CYRILLIC_TO_LATIN, Wine, _token_similarity


TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
VINTAGE_PATTERN = re.compile(r"(?<!\d)(19[5-9]\d|20[0-2]\d)(?!\d)")
STOP_WORDS = {
    "beloe", "butylka", "etiketka", "igristoe", "krasnoe", "rozovoe", "suhoe",
    "vino", "wine", "winery",
}


def extract_label_text(image: np.ndarray) -> str:
    height, width = image.shape[:2]
    scale = min(1.0, 1400 / max(height, width))
    if scale < 1.0:
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    return pytesseract.image_to_string(gray, lang="rus+eng", config="--oem 1 --psm 6")


def extract_year(text: str) -> int | None:
    found = {int(match) for match in VINTAGE_PATTERN.findall(text)}
    if len(found) != 1:
        return None
    return found.pop()


def text_score(text: str, wine: Wine) -> float:
    query_tokens = _tokens(text)
    catalog_tokens = _tokens(f"{wine.name} {wine.winery} {wine.slug}")
    if not query_tokens or not catalog_tokens:
        return 0.0

    matches = 0.0
    for catalog_token in catalog_tokens:
        best = max((_token_similarity(catalog_token, query_token) for query_token in query_tokens), default=0.0)
        if best >= 0.82:
            matches += best
    return min(1.0, matches / len(catalog_tokens))


def _tokens(value: str) -> set[str]:
    normalized = unicodedata.normalize("NFKC", value).casefold().translate(CYRILLIC_TO_LATIN)
    return {
        token
        for token in TOKEN_PATTERN.findall(normalized)
        if len(token) >= 3 and token not in STOP_WORDS
    }
