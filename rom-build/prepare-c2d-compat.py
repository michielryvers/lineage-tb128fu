#!/usr/bin/env python3
"""Add the explicit ARM compiler-helper dependency to pinned Lenovo C2D."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

project = Path(__file__).resolve().parent.parent
root = project / 'build/lineage'
vendor = root / 'vendor/lenovo/sm6225-common'
base = '95347dad2e12199ba852eb31e9d41530de2e66ca'
relative = 'proprietary/vendor/lib/libc2d30_bltlib.so'
patchelf = root / 'prebuilts/extract-tools/linux-x86/bin/patchelf-0_18'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=vendor, text=True).strip()
if head != base:
    raise ValueError(f'Unexpected vendor base: {head}')
original = subprocess.check_output(['git', 'show', f'{base}:{relative}'], cwd=vendor)
target = vendor / relative
with tempfile.TemporaryDirectory(prefix='lenovo-c2d-') as directory:
    candidate = Path(directory) / target.name
    candidate.write_bytes(original)
    subprocess.run([str(patchelf), '--add-needed', 'libshim_c2d.so', str(candidate)], check=True)
    patched = candidate.read_bytes()
    current = target.read_bytes()
    if current not in (original, patched):
        raise ValueError('C2D differs from both the pinned original and expected patched bytes')
    if current != patched:
        target.write_bytes(patched)
    needed = subprocess.check_output([str(patchelf), '--print-needed', str(target)], text=True).splitlines()
    if needed.count('libshim_c2d.so') != 1:
        raise ValueError('Expected exactly one explicit compiler-helper dependency')

record = dict(
    source_commit=base,
    path=relative,
    original_sha256=hashlib.sha256(original).hexdigest(),
    patched_sha256=hashlib.sha256(patched).hexdigest(),
    patched_size=len(patched),
    patchelf_sha256=hashlib.sha256(patchelf.read_bytes()).hexdigest(),
    needed=needed,
    scope='Dependency addition only; shader/GPU donors are unchanged. Final package and runtime C2D checks remain required.',
)
(project / 'build/records/c2d-compat-integration.json').write_text(json.dumps(record, indent=2) + '\n')
print('Pinned ARM32 Lenovo C2D now explicitly depends on libshim_c2d.so')
