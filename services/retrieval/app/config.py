from dataclasses import dataclass
from os import environ


@dataclass(frozen=True)
class Settings:
    database_url: str
    dataset_root: str
    index_path: str
    max_upload_bytes: int


def load_settings() -> Settings:
    database_url = environ.get("DATABASE_URL")
    if not database_url:
        database_url = (
            f"postgresql://{environ.get('PGUSER', 'vinolog')}:"
            f"{environ.get('PGPASSWORD', 'vinolog')}@"
            f"{environ.get('PGHOST', 'db')}:"
            f"{environ.get('PGPORT', '5432')}/"
            f"{environ.get('PGDATABASE', 'vinolog')}"
        )

    return Settings(
        database_url=database_url,
        dataset_root=environ.get("DATASET_ROOT", "/dataset/current"),
        index_path=environ.get("INDEX_PATH", "/indexes/sift-v1.npz"),
        max_upload_bytes=int(environ.get("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024))),
    )

