import unittest

from app.catalog import Media, Wine, media_stem, normalize_key, resolve_references
from app.catalog_browser import catalog_record
from app.index import IndexedReference
from app.ocr import text_score


def wine(**overrides: str) -> Wine:
    values = {
        "slug": "pino-nuar-2025",
        "name": "Пино Нуар, 2025",
        "winery": "Табия",
        "category": "Вино",
        "color": "Красное",
        "region": "Крым",
        "grape_varieties": "Пино Нуар",
        "description": "Описание",
        "image_filename": "DSC00836.webp",
    }
    values.update(overrides)
    return Wine(**values)


class CatalogTest(unittest.TestCase):
    def test_media_stem_removes_strapi_hash(self) -> None:
        self.assertEqual(media_stem("DSC_00836_4070f8fd2f.webp"), "DSC_00836")

    def test_normalize_key_ignores_filename_separators(self) -> None:
        self.assertEqual(normalize_key("DSC_00836"), normalize_key("dsc00836"))

    def test_resolver_prefers_original_image_filename(self) -> None:
        media = [
            Media("thumbnail_DSC_00836_4070f8fd2f.webp", "thumbnail.webp", 10),
            Media("DSC_00836_4070f8fd2f.webp", "original.webp", 100),
        ]

        references = resolve_references([wine()], media)

        self.assertEqual(len(references), 1)
        self.assertEqual(references[0].relative_path, "original.webp")
        self.assertEqual(references[0].mapping_kind, "image_filename")

    def test_wine_card_extracts_year_and_grapes(self) -> None:
        card = wine(grape_varieties="Пино Нуар, Мерло").as_card()

        self.assertEqual(card["year"], 2025)
        self.assertEqual(card["category"], "Вино")
        self.assertEqual(card["color"], "Красное")
        self.assertEqual(card["grapeVarieties"], ["Пино Нуар", "Мерло"])

    def test_ocr_text_breaks_duplicate_image_tie(self) -> None:
        pinot = wine()
        kokur = wine(slug="method-classic-kokur", name="Method Classic Кокур")
        label = "ТАБИЯ Пино Нуар полусухое 2025"

        self.assertGreater(text_score(label, pinot), text_score(label, kokur))

    def test_catalog_record_exposes_image_mapping_diagnostics(self) -> None:
        item = wine()
        reference = IndexedReference(
            wine=item,
            relative_path="pino.webp",
            mapping_kind="image_filename",
            mapping_score=1.0,
        )

        record = catalog_record(item, reference, raw_record_count=2)

        self.assertEqual(record["imageUrl"], "/api/wines/pino-nuar-2025/image")
        self.assertEqual(record["referencePath"], "pino.webp")
        self.assertEqual(record["rawRecordCount"], 2)
        self.assertTrue(record["isIndexed"])


if __name__ == "__main__":
    unittest.main()
