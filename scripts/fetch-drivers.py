#!/usr/bin/env python3
"""Fetch the recorded GPU donors and verify every byte against its source manifest."""
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request

root = Path(__file__).resolve().parent.parent
for manifest in sorted((root / 'provenance/drivers').glob('*.json')):
    data = json.loads(manifest.read_text())
    base = root / 'downloads/drivers' / manifest.stem
    base.mkdir(parents=True, exist_ok=True)
    for item in data['files']:
        rel = Path(item['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError(f'Unsafe path: {rel}')
        if not item['source_url'].startswith('https://raw.githubusercontent.com/'):
            raise ValueError('Unexpected donor source host')
        dest = base / rel
        def valid(path):
            if not path.is_file() or path.stat().st_size != item['size']:
                return False
            with path.open('rb') as stream:
                return hashlib.file_digest(stream, 'sha256').hexdigest() == item['sha256']
        if valid(dest):
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        temp = dest.with_name(dest.name + '.partial')
        try:
            with urllib.request.urlopen(item['source_url'], timeout=120) as response, temp.open('wb') as stream:
                shutil.copyfileobj(response, stream)
            if not valid(temp):
                raise ValueError(f'Donor hash/size mismatch: {rel}')
            temp.replace(dest)
        finally:
            temp.unlink(missing_ok=True)
    shutil.copy2(manifest, base / 'manifest.json')
    print(f'Verified {manifest.stem}: {len(data["files"])} files')
