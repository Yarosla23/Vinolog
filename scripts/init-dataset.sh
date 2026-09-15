#!/bin/sh
set -eu

input=/input
output=/dataset
ready="$output/current/.ready"

if [ -f "$ready" ] && [ -f "$output/current/catalog/strapi_output0709.csv" ] && [ -d "$output/current/uploads" ] && [ -d "$output/current/eval/queries" ]; then
  manifest="$output/current/catalog/uploads.csv"
  if [ ! -f "$manifest" ]; then
    echo 'Indexing media in the existing dataset volume...'
    python3 /usr/local/bin/build-media-manifest.py "$output/current/uploads" "$manifest.tmp"
    mv "$manifest.tmp" "$manifest"
  fi
  echo 'Dataset already initialized; using the existing volume.'
  exit 0
fi

for filename in prod-svoe-vino-strapi.part1.rar prod-svoe-vino-strapi.part2.rar prod-svoe-vino-strapi.part3.rar strapi_output0709.csv eval.zip; do
  if [ ! -f "$input/$filename" ]; then
    echo "Missing $input/$filename. Place all dataset files in data/dataset/." >&2
    exit 1
  fi
done

work="$output/.initializing"
rm -rf "$work"
mkdir -p "$work/rar" "$work/catalog" "$work/eval"

echo 'Extracting Strapi uploads (first startup only)...'
unrar x -idq -o+ "$input/prod-svoe-vino-strapi.part1.rar" "$work/rar/"
uploads="$work/rar/prod-svoe-vino-strapi/prod-svoe-vino/strapi/uploads"
if [ ! -d "$uploads" ]; then
  echo 'RAR extraction did not produce the expected Strapi uploads directory.' >&2
  exit 1
fi

cp "$input/strapi_output0709.csv" "$work/catalog/"
unzip -q "$input/eval.zip" -d "$work/eval"
if [ ! -d "$work/eval/queries" ]; then
  echo 'Eval archive did not produce the expected queries directory.' >&2
  exit 1
fi

mv "$uploads" "$work/uploads"
python3 /usr/local/bin/build-media-manifest.py "$work/uploads" "$work/catalog/uploads.csv"
rm -rf "$work/rar"
touch "$work/.ready"
if [ -e "$output/current" ]; then
  echo 'An incomplete dataset exists in the volume. Remove the dataset volume to import again.' >&2
  exit 1
fi
mv "$work" "$output/current"
echo 'Dataset initialized in the persistent volume.'
