#!/bin/sh
set -eu

if [ ! -f /input/strapi_output0709.csv ] || [ ! -f /dataset/current/catalog/uploads.csv ]; then
  echo 'Catalog CSV or media manifest is missing; run dataset-init first.' >&2
  exit 1
fi

catalog_sha256="$(sha256sum /input/strapi_output0709.csv | cut -d ' ' -f 1)"
if [ "$(psql -Atqc "SELECT to_regclass('public.dataset_imports') IS NOT NULL")" = t ]; then
  imported_sha256="$(psql -Atqc "SELECT catalog_sha256 FROM dataset_imports WHERE version = 'dataset-v1'")"
  if [ -n "$imported_sha256" ]; then
    if [ "$imported_sha256" != "$catalog_sha256" ]; then
      echo 'Catalog CSV changed since import. Use a fresh database volume to import a new dataset.' >&2
      exit 1
    fi
    echo 'Database already contains this dataset; skipping import.'
    exit 0
  fi
fi

echo 'Importing catalog and media index into PostgreSQL...'
psql -v ON_ERROR_STOP=1 -v catalog_sha256="$catalog_sha256" -f /import/import-dataset.sql
echo 'Database import completed.'
