from pathlib import Path

from .catalog import load_catalog, resolve_references
from .config import load_settings
from .image_features import extract_features, read_image
from .index import IndexedReference, save_index


def main() -> None:
    settings = load_settings()
    output = Path(settings.index_path)
    if output.exists():
        print(f"Retrieval index already exists: {output}")
        return

    wines, media = load_catalog(settings.database_url)
    resolved = resolve_references(wines, media)
    print(f"Resolved {len(resolved)} references for {len(wines)} catalog wines.")

    indexed_references: list[IndexedReference] = []
    features = []
    uploads = Path(settings.dataset_root) / "uploads"
    for position, reference in enumerate(resolved, start=1):
        path = uploads / reference.relative_path
        try:
            item_features = extract_features(read_image(str(path)), max_side=1200, feature_count=700)
        except ValueError as error:
            print(error)
            continue
        if len(item_features.descriptors) < 8:
            continue

        indexed_references.append(IndexedReference(
            wine=reference.wine,
            relative_path=reference.relative_path,
            mapping_kind=reference.mapping_kind,
            mapping_score=reference.mapping_score,
        ))
        features.append(item_features)
        if position % 100 == 0:
            print(f"Processed {position}/{len(resolved)} references.")

    if not features:
        raise SystemExit("No usable reference images were indexed.")
    save_index(settings.index_path, indexed_references, features)
    print(f"Saved {len(features)} references to {settings.index_path}.")


if __name__ == "__main__":
    main()

