#!/usr/bin/env python3
"""Materialize and verify the pinned ARM64 WebView before starting Android."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

project = Path(__file__).resolve().parent.parent
source = project / 'build/lineage'
relative = 'external/chromium-webview/prebuilt/arm64'
repo = source / relative
entry = next(p for p in ET.parse(project / 'build/records/source-manifest.xml').getroot()
             if p.tag == 'project' and p.get('path') == relative)
revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
if revision != entry.get('revision'):
    raise SystemExit('WebView revision differs from the pinned source manifest')
pointer = subprocess.check_output(['git', 'show', 'HEAD:webview.apk'], cwd=repo)
match = re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\n'
                     rb'oid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n', pointer)
if not match:
    raise SystemExit('Pinned WebView is not the expected Git LFS pointer format')
expected_hash, expected_size = match[1].decode(), int(match[2])
apk = repo / 'webview.apk'
if apk.stat().st_size == len(pointer) and apk.read_bytes() == pointer:
    subprocess.run([
        'docker', 'run', '--rm', '--user', f'{os.getuid()}:{os.getgid()}',
        '-e', 'HOME=/builder-home',
        '-v', f'{project / "build/home"}:/builder-home',
        '-v', f'{source}:/src', '-w', f'/src/{relative}',
        'lenovo-lineage-build:24.04',
        'git', 'lfs', 'pull', '--include=webview.apk', 'github',
    ], check=True)
with apk.open('rb') as stream:
    actual_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
if apk.stat().st_size != expected_size or actual_hash != expected_hash:
    raise SystemExit('WebView APK does not match its pinned Git LFS hash and size')
with zipfile.ZipFile(apk) as archive:
    if archive.testzip() is not None or 'AndroidManifest.xml' not in archive.namelist():
        raise SystemExit('WebView APK ZIP validation failed')
record = dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              path=relative + '/webview.apk', revision=revision,
              sha256=actual_hash, size=expected_size, zip_crc_valid=True)
(project / 'build/records/webview-preflight.json').write_text(json.dumps(record, indent=2) + '\n')
print(f'Pinned ARM64 WebView verified: {expected_size} bytes, SHA-256 {actual_hash}')
