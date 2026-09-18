#!/usr/bin/env python3
"""Keep the pinned ARM32 C2D client with its compatible GSL dependency."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

project = Path(__file__).resolve().parent.parent
root = project / 'build/lineage'
vendor = root / 'vendor/lenovo/sm6225-common'
base = '95347dad2e12199ba852eb31e9d41530de2e66ca'
patchelf = root / 'prebuilts/extract-tools/linux-x86/bin/patchelf-0_18'
if subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=vendor, text=True).strip() != base:
    raise ValueError('Unexpected Lenovo vendor base')

files = []
with tempfile.TemporaryDirectory(prefix='lenovo-c2d-gsl-') as directory:
    for source, destination, options in [
        ('libgsl.so', 'libgsl_c2d.so', ['--set-soname', 'libgsl_c2d.so']),
        ('libC2D2.so', 'libC2D2.so', ['--replace-needed', 'libgsl.so', 'libgsl_c2d.so']),
    ]:
        source_path = 'proprietary/vendor/lib/' + source
        destination_path = 'proprietary/vendor/lib/' + destination
        original = subprocess.check_output(['git', 'show', f'{base}:{source_path}'], cwd=vendor)
        candidate = Path(directory) / destination
        candidate.write_bytes(original)
        subprocess.run([str(patchelf), *options, str(candidate)], check=True)
        patched = candidate.read_bytes()
        target = vendor / destination_path
        if target.exists() and target.read_bytes() not in (original, patched):
            raise ValueError(f'Unexpected existing bytes: {target}')
        target.write_bytes(patched)
        files.append(dict(path=destination_path, source_path=source_path,
                          original_sha256=hashlib.sha256(original).hexdigest(),
                          sha256=hashlib.sha256(patched).hexdigest(), size=len(patched),
                          patchelf_options=options))

record = dict(source_commit=base, files=files,
              patchelf_sha256=hashlib.sha256(patchelf.read_bytes()).hexdigest(),
              scope='ARM32 C2D only. Main GSL/GLES and all ARM64 libraries unchanged.')
(project / 'build/records/c2d-gsl-integration.json').write_text(json.dumps(record, indent=2) + '\n')
print('Prepared private pinned ARM32 GSL for C2D')
