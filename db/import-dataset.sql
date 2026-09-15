BEGIN;

CREATE TABLE wine_catalog_raw (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text,
  category text,
  color text,
  region text,
  grape_varieties text,
  description text,
  winery text,
  slug text,
  image_filename text
);

\copy wine_catalog_raw (name, category, color, region, grape_varieties, description, winery, slug, image_filename) FROM '/input/strapi_output0709.csv' WITH (FORMAT csv, HEADER true)

CREATE INDEX wine_catalog_raw_slug_idx ON wine_catalog_raw (slug);

CREATE VIEW wine_catalog AS
SELECT DISTINCT ON (slug)
  slug, name, category, color, region, grape_varieties, description, winery, image_filename
FROM wine_catalog_raw
WHERE slug IS NOT NULL AND btrim(slug) <> ''
ORDER BY slug, id;

CREATE TABLE wine_media (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  filename text NOT NULL,
  relative_path text NOT NULL UNIQUE,
  size_bytes bigint NOT NULL
);

\copy wine_media (filename, relative_path, size_bytes) FROM '/dataset/current/catalog/uploads.csv' WITH (FORMAT csv, HEADER true)

CREATE INDEX wine_media_filename_idx ON wine_media (filename);

CREATE TABLE dataset_imports (
  version text PRIMARY KEY,
  catalog_sha256 text NOT NULL,
  catalog_rows bigint NOT NULL,
  media_rows bigint NOT NULL,
  imported_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO dataset_imports (version, catalog_sha256, catalog_rows, media_rows)
SELECT 'dataset-v1', :'catalog_sha256',
  (SELECT count(*) FROM wine_catalog_raw),
  (SELECT count(*) FROM wine_media);

COMMIT;
