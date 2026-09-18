#!/usr/bin/env python3
"""Stage the newest verified GPU candidate in an isolated Android checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('android_root', type=Path)
args = p.parse_args()
project = Path(__file__).resolve().parent.parent
vendor = args.android_root / 'vendor/lenovo/sm6225-common'
listing = args.android_root / 'device/lenovo/sm6225-common/proprietary-files.txt'
text = listing.read_text()
selected = {}
# Keep the complete 64-bit tapas stack. The A05s provides the newest verified
# 32-bit candidate. Shared KBC data comes from tapas and requires runtime checks.
for donor, prefix in [
    ('adreno-samsung-615.76', 'proprietary/vendor/lib/'),
    ('adreno-samsung-615.76-dependencies', 'proprietary/vendor/lib/'),
    ('adreno-tapas-615.98', 'proprietary/'),
    ('adreno-tapas-615.98-dependencies', 'proprietary/'),
]:
    base = project / 'downloads/drivers' / donor
    manifest = json.loads((base / 'manifest.json').read_text())
    for entry in manifest['files']:
        if not entry['path'].startswith(prefix):
            continue
        rel = Path(entry['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError(f'Unsafe path: {rel}')
        data = (base / rel).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry['sha256'], rel
        dest = vendor / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(base / rel, dest)
        selected[str(rel)] = dict(donor=donor, **entry)

existing = {line.lstrip('-').split(';')[0].split('|')[0]
            for line in text.splitlines() if line and not line.startswith('#')}
added = sorted(str(Path(path).relative_to('proprietary'))
               for path in selected if str(Path(path).relative_to('proprietary')) not in existing)
if added:
    text += '\n# Additional files for Adreno 615.98 arm64 / 615.76 arm candidate\n'
    text += '\n'.join(added) + '\n'
listing.write_text(text)
record = dict(status='Experimental; allocation, rendering and shared KBC compatibility need device validation',
              arm64='615.98 tapas', arm='615.76 A05s', shared_kbc='615.98 tapas',
              retained='Lenovo C2D and legacy optional tooling not supplied by either donor',
              files=list(selected.values()))
out = project / 'build/records/gpu-integration.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(record, indent=2) + '\n')
print(f'Staged {len(selected)} verified files; added {len(added)} blob-list entries')
