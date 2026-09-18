#!/usr/bin/env bash
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
command -v repo >/dev/null
mkdir -p "$project_root/build/lineage" "$project_root/build/records"
rm -f "$project_root/build/records/sync-completed.txt"
cd "$project_root/build/lineage"
# Use this local, versioned manifest checkout so a sync cannot silently advance it.
repo init -u "$project_root" -b "$(git -C "$project_root" rev-parse HEAD)" -m default.xml
repo sync -c -j"${SYNC_JOBS:-8}" --no-clone-bundle --no-tags --fail-fast
repo manifest -r -o ../records/source-manifest.xml
date -Is > ../records/sync-completed.txt
