#!/usr/bin/env bash
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
test -f "$project_root/build/records/source-integration.json"
mkdir -p "$project_root/build/home"
python3 "$project_root/rom-build/prepare-webview.py"
docker run --rm --name lenovo-lineage-rom --user "$(id -u):$(id -g)" \
  --cpus="${BUILD_JOBS:-8}" --memory="${BUILD_MEMORY:-20g}" --memory-swap="${BUILD_MEMORY_SWAP:-40g}" \
  -e HOME=/builder-home \
  -e GOGC=25 -e GOMEMLIMIT="${GO_MEMORY_LIMIT:-14GiB}" -e BUILD_JOBS="${BUILD_JOBS:-8}" \
  -e NINJA_HIGHMEM_NUM_JOBS=1 \
  -v "$project_root/build/home:/builder-home" \
  -v "$project_root/build/lineage:/src" \
  -w /src lenovo-lineage-build:24.04 bash -c '
    set -eo pipefail
    source build/envsetup.sh
    source vendor/lineage/vars/aosp_target_release
    lunch "lineage_tb128fu-${aosp_target_release}-userdebug"
    m -j"$BUILD_JOBS" bacon
  '
date -Is > "$project_root/build/records/rom-build-completed.txt"
