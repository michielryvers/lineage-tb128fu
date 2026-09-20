#!/usr/bin/env bash
# Source after setting project_root. Keep build memory budgets from stacking.
mkdir -p "$project_root/build/records"
exec 9>"$project_root/build/records/host-build.lock"
if ! flock -n 9; then
  echo 'Another Lenovo build/test is running; wait for it to finish.' >&2
  exit 2
fi
# A Docker container can survive the loss of its launching terminal and lock.
active_builds=$(docker ps --filter 'name=^/lenovo-' --format '{{.Names}}')
if [[ -n "$active_builds" ]]; then
  echo "Existing Lenovo container must finish first: $active_builds" >&2
  exit 2
fi
