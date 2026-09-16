from __future__ import annotations

from dataclasses import dataclass, replace
import time
from urllib.parse import quote

import numpy as np

from .index import Candidate, SearchResult, SiftIndex
from .ocr import extract_label_text, extract_year, text_score


SHORTLIST_LIMIT = 50
RESPONSE_LIMIT = 5


@dataclass(frozen=True)
class ProductResult:
    body: dict[str, object]


def _wine_card_with_image(candidate: Candidate) -> dict[str, object]:
    card = candidate.wine.as_card()
    card["imageUrl"] = f"/api/wines/{quote(candidate.wine.slug, safe='')}/image"
    return card


def filter_by_year(candidates: list[Candidate], year: int | None) -> list[Candidate]:
    if year is None:
        return list(candidates)
    matching = [item for item in candidates if str(year) in f"{item.wine.name} {item.wine.slug}"]
    return matching or list(candidates)


class SearchService:
    def __init__(self, index: SiftIndex) -> None:
        self.index = index

    def search(self, image: np.ndarray) -> ProductResult:
        started = time.perf_counter()
        result = self.index.search(image, limit=SHORTLIST_LIMIT)
        ocr_started = time.perf_counter()
        label_text = extract_label_text(image)
        ocr_ms = round((time.perf_counter() - ocr_started) * 1000)
        candidates = [
            replace(
                candidate,
                score=round(min(1.0, candidate.score + (0.2 * text_score(label_text, candidate.wine))), 4),
            )
            for candidate in filter_by_year(result.candidates, extract_year(label_text))
        ]
        candidates.sort(key=lambda item: (item.score, item.inliers, item.good_matches), reverse=True)
        result = replace(result, candidates=candidates[:RESPONSE_LIMIT])
        total_ms = round((time.perf_counter() - started) * 1000)
        return ProductResult(self._product_body(result, total_ms, ocr_ms))

    @staticmethod
    def _product_body(result: SearchResult, total_ms: int, ocr_ms: int) -> dict[str, object]:
        candidates = result.candidates
        top_score = candidates[0].score if candidates else 0.0
        second_score = candidates[1].score if len(candidates) > 1 else 0.0
        margin = max(0.0, top_score - second_score)
        top = candidates[0] if candidates else None
        wine_card = top.wine.as_card() if top else None
        if wine_card:
            wine_card["imageUrl"] = f"/api/wines/{quote(top.wine.slug, safe='')}/image"
        alternatives = [_wine_card_with_image(item) for item in candidates[1:4]]

        if top and top.inliers >= 7 and top.good_matches >= 10 and top_score >= 0.3:
            status = "matched"
        elif top and top.good_matches >= 5 and top_score >= 0.12:
            status = "uncertain"
        else:
            status = "not_found"

        guidance = None
        if status == "uncertain":
            guidance = "Приблизьте этикетку, уберите блик и убедитесь, что название и год попали в кадр."
        elif status == "not_found":
            guidance = "Совпадение не подтверждено. Снимите этикетку крупнее и строго спереди."

        return {
            "status": status,
            "wine": wine_card if status == "matched" else None,
            "candidates": [{"slug": item.wine.slug, "score": item.score} for item in candidates],
            "confidence": {
                "kind": "similarity",
                "top1Score": top_score,
                "margin": round(margin, 4),
            },
            "timing": {
                "totalMs": total_ms,
                "stages": {
                    "features": result.feature_ms,
                    "search": result.search_ms,
                    "ocr": ocr_ms,
                },
            },
            "alternatives": alternatives,
            "version": {
                "model": "sift-ransac-ocr-v1",
                "catalog": "dataset-v1",
                "configuration": "sift-700-flann-ransac-tesseract",
            },
            **({"guidance": guidance} if guidance else {}),
            "isMock": False,
        }
