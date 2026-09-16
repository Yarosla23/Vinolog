from __future__ import annotations

from math import ceil
from urllib.parse import quote

import psycopg
from psycopg.rows import dict_row

from .catalog import Wine
from .index import IndexedReference, SiftIndex


def catalog_record(
    wine: Wine,
    reference: IndexedReference | None,
    raw_record_count: int,
) -> dict[str, object]:
    card = wine.as_card()
    if reference:
        card["imageUrl"] = f"/api/wines/{quote(wine.slug, safe='')}/image"

    return {
        **card,
        "imageFilename": wine.image_filename,
        "referencePath": reference.relative_path if reference else None,
        "mappingKind": reference.mapping_kind if reference else None,
        "mappingScore": round(reference.mapping_score, 4) if reference else None,
        "rawRecordCount": raw_record_count,
        "isIndexed": reference is not None,
    }


class CatalogBrowser:
    def __init__(self, database_url: str, index: SiftIndex) -> None:
        self.database_url = database_url
        self.references = {item.wine.slug: item for item in index.references}

    def browse(
        self,
        *,
        query: str,
        page: int,
        per_page: int,
        image_status: str,
    ) -> dict[str, object]:
        conditions: list[str] = []
        parameters: list[object] = []
        normalized_query = query.strip()

        if normalized_query:
            conditions.append(
                "concat_ws(' ', wc.slug, wc.name, wc.winery, wc.category, wc.color, "
                "wc.region, wc.grape_varieties) ILIKE %s"
            )
            parameters.append(f"%{normalized_query}%")

        indexed_slugs = list(self.references)
        if image_status == "indexed":
            conditions.append("wc.slug = ANY(%s)")
            parameters.append(indexed_slugs)
        elif image_status == "missing":
            conditions.append("NOT (wc.slug = ANY(%s))")
            parameters.append(indexed_slugs)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        offset = (page - 1) * per_page
        parameters.extend([per_page, offset])

        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            summary = connection.execute(
                """
                SELECT
                  (SELECT count(*) FROM wine_catalog_raw) AS raw_records,
                  (SELECT count(*) FROM wine_catalog) AS unique_wines,
                  (SELECT count(*) FROM (
                    SELECT slug FROM wine_catalog_raw
                    WHERE slug IS NOT NULL AND btrim(slug) <> ''
                    GROUP BY slug HAVING count(*) > 1
                  ) duplicates) AS duplicate_slugs,
                  (SELECT count(*) FROM wine_media) AS media_files
                """
            ).fetchone()
            rows = connection.execute(
                f"""
                WITH catalog AS (
                  SELECT wc.*, counts.raw_record_count
                  FROM wine_catalog wc
                  JOIN (
                    SELECT slug, count(*) AS raw_record_count
                    FROM wine_catalog_raw
                    GROUP BY slug
                  ) counts USING (slug)
                  {where_clause}
                )
                SELECT *, count(*) OVER() AS total_count
                FROM catalog
                ORDER BY winery, name, slug
                LIMIT %s OFFSET %s
                """,
                parameters,
            ).fetchall()

        total_items = int(rows[0]["total_count"]) if rows else 0
        wines = []
        for row in rows:
            wine = Wine(
                slug=row["slug"],
                name=row["name"] or "Без названия",
                winery=row["winery"] or "Производитель не указан",
                image_filename=row["image_filename"] or "",
                category=row["category"],
                color=row["color"],
                region=row["region"],
                grape_varieties=row["grape_varieties"],
                description=row["description"],
            )
            wines.append(catalog_record(
                wine,
                self.references.get(wine.slug),
                int(row["raw_record_count"]),
            ))

        unique_wines = int(summary["unique_wines"])
        indexed_wines = len(self.references)
        return {
            "summary": {
                "rawRecords": int(summary["raw_records"]),
                "uniqueWines": unique_wines,
                "duplicateSlugs": int(summary["duplicate_slugs"]),
                "mediaFiles": int(summary["media_files"]),
                "indexedWines": indexed_wines,
                "missingFromIndex": max(0, unique_wines - indexed_wines),
            },
            "wines": wines,
            "pagination": {
                "page": page,
                "perPage": per_page,
                "totalItems": total_items,
                "totalPages": ceil(total_items / per_page) if total_items else 0,
            },
        }
