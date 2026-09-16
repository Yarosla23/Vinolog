from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

import psycopg
from psycopg.rows import dict_row


DERIVATIVE_PREFIXES = ("thumbnail_", "small_", "medium_", "large_")
HASH_SUFFIX = re.compile(r"_[0-9a-f]{10}$", re.IGNORECASE)
TOKEN_PATTERN = re.compile(r"[a-zа-яё0-9]+", re.IGNORECASE)
YEAR_PATTERN = re.compile(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)")

CYRILLIC_TO_LATIN = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
    "ё": "e", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
})


@dataclass(frozen=True)
class Wine:
    slug: str
    name: str
    winery: str
    image_filename: str
    category: str | None = None
    color: str | None = None
    region: str | None = None
    grape_varieties: str | None = None
    description: str | None = None

    def as_card(self) -> dict[str, object]:
        year_match = YEAR_PATTERN.search(self.name)
        grapes = [item.strip() for item in (self.grape_varieties or "").split(",") if item.strip()]
        return {
            "slug": self.slug,
            "name": self.name.strip(),
            "producer": self.winery.strip(),
            "year": int(year_match.group(1)) if year_match else None,
            "category": self.category.strip() if self.category and self.category.strip() else None,
            "color": self.color.strip() if self.color and self.color.strip() else None,
            "region": self.region.strip() if self.region and self.region.strip() else None,
            "grapeVarieties": grapes,
            "description": self.description.strip() if self.description and self.description.strip() else None,
            "servingTemperature": None,
            "imageUrl": None,
        }


@dataclass(frozen=True)
class Media:
    filename: str
    relative_path: str
    size_bytes: int


@dataclass(frozen=True)
class Reference:
    wine: Wine
    relative_path: str
    mapping_kind: str
    mapping_score: float


def _stem(filename: str) -> str:
    return Path(filename).stem


def normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def latin_tokens(value: str) -> set[str]:
    normalized = unicodedata.normalize("NFKC", value).casefold().translate(CYRILLIC_TO_LATIN)
    return {
        token
        for token in TOKEN_PATTERN.findall(normalized)
        if len(token) >= 3
        and not token.isdigit()
        and token not in {
            "beloe", "butylka", "etiketka", "foto", "igristoe", "krasnoe",
            "normal", "photo", "preview", "rozovoe", "suhoe", "vino", "wine",
            "winery",
        }
    }


def media_stem(filename: str) -> str:
    return HASH_SUFFIX.sub("", _stem(filename))


def is_original_media(filename: str) -> bool:
    return (
        not filename.startswith(DERIVATIVE_PREFIXES)
        and Path(filename).suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp"}
    )


def _fuzzy_score(wine: Wine, media_words: set[str]) -> float:
    catalog_words = latin_tokens(f"{wine.slug} {_stem(wine.image_filename)} {wine.name} {wine.winery}")
    if not media_words or not catalog_words:
        return 0.0

    matches = 0.0
    for media_word in media_words:
        best = max((_token_similarity(media_word, catalog_word) for catalog_word in catalog_words), default=0.0)
        if best >= 0.82:
            matches += best

    coverage = matches / len(media_words)
    precision = matches / len(catalog_words)
    return (0.8 * coverage) + (0.2 * precision)


def _token_similarity(left: str, right: str) -> float:
    if left == right:
        return 1.0
    if min(len(left), len(right)) < 5:
        return 0.0

    from difflib import SequenceMatcher

    return SequenceMatcher(None, left, right).ratio()


def resolve_references(wines: list[Wine], media: list[Media]) -> list[Reference]:
    originals = [item for item in media if is_original_media(item.filename)]
    by_key: dict[str, list[Media]] = {}
    for item in originals:
        by_key.setdefault(normalize_key(media_stem(item.filename)), []).append(item)

    references: list[Reference] = []
    used_paths: set[str] = set()
    unresolved: list[Wine] = []

    for wine in wines:
        image_matches = by_key.get(normalize_key(_stem(wine.image_filename)), [])
        slug_matches = by_key.get(normalize_key(wine.slug), [])
        matches = image_matches or slug_matches
        if not matches:
            unresolved.append(wine)
            continue

        selected = max(matches, key=lambda item: item.size_bytes)
        used_paths.add(selected.relative_path)
        references.append(Reference(
            wine=wine,
            relative_path=selected.relative_path,
            mapping_kind="image_filename" if image_matches else "slug",
            mapping_score=1.0,
        ))

    available_media = [item for item in originals if item.relative_path not in used_paths]
    media_by_path = {item.relative_path: item for item in available_media}
    media_tokens = {
        item.relative_path: latin_tokens(media_stem(item.filename))
        for item in available_media
    }
    paths_by_token: dict[str, set[str]] = {}
    for path, tokens in media_tokens.items():
        for token in tokens:
            paths_by_token.setdefault(token, set()).add(path)

    for wine in unresolved:
        catalog_tokens = latin_tokens(f"{wine.slug} {_stem(wine.image_filename)} {wine.name} {wine.winery}")
        candidate_paths: set[str] = set()
        for token in catalog_tokens:
            candidate_paths.update(paths_by_token.get(token, set()))
        candidates = [media_by_path[path] for path in candidate_paths if path not in used_paths]
        scored = sorted(
            ((_fuzzy_score(wine, media_tokens[item.relative_path]), item) for item in candidates),
            key=lambda pair: pair[0],
            reverse=True,
        )
        if not scored or scored[0][0] < 0.72:
            continue

        score, selected = scored[0]
        used_paths.add(selected.relative_path)
        references.append(Reference(
            wine=wine,
            relative_path=selected.relative_path,
            mapping_kind="fuzzy_filename",
            mapping_score=score,
        ))

    return references


def load_catalog(database_url: str) -> tuple[list[Wine], list[Media]]:
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        wine_rows = connection.execute(
            """
            SELECT slug, name, winery, image_filename, category, color,
                   region, grape_varieties, description
            FROM wine_catalog
            ORDER BY slug
            """
        ).fetchall()
        media_rows = connection.execute(
            """
            SELECT filename, relative_path, size_bytes
            FROM wine_media
            ORDER BY relative_path
            """
        ).fetchall()

    wines = [Wine(**row) for row in wine_rows]
    media = [Media(**row) for row in media_rows]
    return wines, media
