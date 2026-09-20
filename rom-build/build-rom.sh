#!/usr/bin/env bash
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source "$project_root/rom-build/build-lock.sh"
test -f "$project_root/build/records/source-integration.json"
mkdir -p "$project_root/build/home"
python3 "$project_root/rom-build/prepare-webview.py"
docker run --rm --name lenovo-lineage-rom --user "$(id -u):$(id -g)" \
  --cpus=2 --cpuset-cpus=0-1 --memory=10g --memory-swap=12g \
  -e HOME=/builder-home \
  -e GOGC=25 -e GOMEMLIMIT=6GiB \
  -e NINJA_HIGHMEM_NUM_JOBS=1 \
  -v "$project_root/build/home:/builder-home" \
  -v "$project_root/build/lineage:/src" \
  -v "$project_root/rom-build:/recipe:ro" \
  -w /src lenovo-lineage-build:24.04 bash -c '
    set -eo pipefail
    source build/envsetup.sh
    source vendor/lineage/vars/aosp_target_release
    lunch "lineage_tb128fu-${aosp_target_release}-userdebug"
    m -j1 --skip-ninja bacon
    python3 /recipe/build-target-closure.py --label build-rom bacon
  '
date -Is > "$project_root/build/records/rom-build-completed.txt"
