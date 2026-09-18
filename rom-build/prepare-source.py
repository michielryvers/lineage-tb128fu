#!/usr/bin/env python3
"""Apply the reviewed TB128FU integration after the pinned repo sync completes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

project = Path(__file__).resolve().parent.parent
root = project / 'build/lineage'
records = project / 'build/records'
patches = project / 'rom-build/patches'
if not (records / 'sync-completed.txt').exists():
    sys.exit('Source sync has not completed successfully')

bases = json.loads((patches / 'revisions.json').read_text())
forks = json.loads((project / 'provenance/forks.json').read_text())
for item in forks:
    cwd = root / item['path']
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd, text=True).strip()
    if head != item['revision']:
        sys.exit(f"Unexpected source revision for {item['path']}: {head}")
plan = [
    ('system/update_engine', 'update-engine-recovery-vabc-remap.patch', bases['update-engine']['base']),
    ('build/soong', 'soong-host-memory.patch', bases['soong']['base']),
    ('prebuilts/clang/host/linux-x86', 'clang-c2d-builtins-visibility.patch', bases['clang-prebuilts']['base']),
    ('hardware/qcom-caf/sm8250/audio', 'audio-prebuilt-stack-selection.patch', bases['qcom-audio']['base']),
]
# Later patches may edit a hunk introduced by an earlier patch. Recognize an
# exact fully-patched tree through an isolated index instead of expecting each
# earlier patch to reverse-apply independently through subsequent changes.
complete = set()
for path in dict.fromkeys(item[0] for item in plan):
    cwd = root / path
    base = next(item[2] for item in plan if item[0] == path)
    with tempfile.TemporaryDirectory(prefix='lenovo-source-check-') as directory:
        env = {**os.environ, 'GIT_INDEX_FILE': str(Path(directory) / 'index')}
        def git_index(*arguments):
            return subprocess.check_output(['git', *arguments], cwd=cwd, env=env)
        git_index('read-tree', base)
        for repo, name, _ in plan:
            if repo == path:
                git_index('apply', '--cached', str(patches / name))
        changed = git_index('diff', '--cached', '--name-only', base).decode().splitlines()
        matches = True
        for name in changed:
            entry = git_index('ls-files', '--', name)
            actual = cwd / name
            if not entry:
                matches &= not actual.exists()
            else:
                matches &= actual.is_file() and actual.read_bytes() == git_index('show', ':' + name)
        if matches:
            complete.add(path)
applied = []
for path, name, base in plan:
    cwd = root / path
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd, text=True).strip()
    if head != base:
        sys.exit(f'Unexpected base for {path}: {head}, expected {base}')
    patch = patches / name
    check = subprocess.run(['git', 'apply', '--reverse', '--check', str(patch)],
                           cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if path not in complete and check.returncode:
        subprocess.run(['git', 'apply', '--check', str(patch)], cwd=cwd, check=True)
        subprocess.run(['git', 'apply', str(patch)], cwd=cwd, check=True)
    applied.append(dict(path=path, patch=name, sha256=hashlib.sha256(patch.read_bytes()).hexdigest()))

vendor = root / 'vendor/lenovo/sm6225-common/proprietary'
for path in ['framework/tcmclient.jar', 'etc/permissions/privapp-permissions-qti.xml',
             'etc/sysconfig/qti_whitelist.xml']:
    dest = vendor / 'system' / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(vendor / path, dest)

subprocess.run([sys.executable, str(project / 'rom-build/integrate-gpu.py'), str(root)], check=True)
subprocess.run([sys.executable, str(project / 'rom-build/prepare-c2d-compat.py')], check=True)
subprocess.run([sys.executable, str(project / 'rom-build/prepare-c2d-gsl.py')], check=True)
subprocess.run([sys.executable, 'extract-files.py', '--regenerate_makefiles'],
               cwd=root / 'device/lenovo/tb128fu', check=True,
               env={**os.environ, 'PYTHONPATH': '../../../tools/extract-utils'})
(records / 'source-integration.json').write_text(json.dumps(applied, indent=2) + '\n')
print('Source integration prepared; full Android build validation is next')
