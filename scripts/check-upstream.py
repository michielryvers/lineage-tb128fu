#!/usr/bin/env python3
"""Report moving upstream heads without changing any source or pinned revision."""
import json
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent.parent
failed = False
for item in json.loads((root / 'provenance/upstreams.json').read_text()):
    try:
        result = subprocess.check_output(['git', 'ls-remote', '--exit-code', item['url'],
                                          'refs/heads/' + item['branch']], text=True, timeout=90)
        revision = result.split()[0]
        status = 'unchanged' if revision == item['revision'] else 'REVIEW NEEDED'
        print(f'{item["name"]}: {status} ({item["revision"][:12]} -> {revision[:12]})')
    except (subprocess.SubprocessError, IndexError) as error:
        failed = True
        print(f'{item["name"]}: unable to check: {error}', file=sys.stderr)
sys.exit(1 if failed else 0)
