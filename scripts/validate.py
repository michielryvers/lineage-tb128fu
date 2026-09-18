#!/usr/bin/env python3
"""Check syntax and consistency of the published source recipe; does not build Android."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
root = Path(__file__).resolve().parent.parent
for directory in ('scripts', 'rom-build'):
    for path in (root / directory).rglob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for path in (root / directory).rglob('*.sh'):
        subprocess.run(['bash', '-n', str(path)], check=True)
manifest = ET.parse(root / 'manifests/pinned.xml').getroot()
remotes = {e.get('name'): e.get('fetch') for e in manifest.findall('remote')}
assert all(url.startswith('https://') for url in remotes.values())
projects = {e.get('path', e.get('name')): e for e in manifest.findall('project')}
assert len(projects) == len(manifest.findall('project'))
for item in projects.values():
    assert re.fullmatch('[0-9a-f]{40}', item.get('revision', '')), item.attrib
for item in json.loads((root / 'provenance/forks.json').read_text()):
    entry = projects[item['path']]
    assert entry.get('revision') == item['revision']
    assert entry.get('name') == 'michielryvers/' + item['name']
for path in (root / 'provenance/drivers').glob('*.json'):
    for item in json.loads(path.read_text())['files']:
        assert re.fullmatch('[0-9a-f]{64}', item['sha256'])
        assert item['size'] > 0
        assert item['source_url'].startswith('https://raw.githubusercontent.com/')
        assert not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts
print(f'Validated script syntax, {len(projects)} source pins, fork revisions and donor metadata')
