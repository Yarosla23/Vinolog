import csv
import sys
from pathlib import Path

uploads = Path(sys.argv[1])
output = Path(sys.argv[2])
media = sorted(path for path in uploads.rglob('*') if path.is_file())
if not media:
    raise SystemExit('No Strapi media files found.')

with output.open('w', encoding='utf-8', newline='') as stream:
    writer = csv.writer(stream)
    writer.writerow(['filename', 'relative_path', 'size_bytes'])
    for path in media:
        writer.writerow([path.name, path.relative_to(uploads).as_posix(), path.stat().st_size])
