#!/usr/bin/env bash
# Daily L3 collection. flock is held across collection and report writes.
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
export PYTHONPATH="$PWD/src"
exec 9>"/tmp/goodsdex-release-dates.lock"
flock -n 9 || exit 0
PYTHON_BIN="${GOODSDEX_PYTHON:-python3}"
"$PYTHON_BIN" scripts/release_dates_run.py --lane L3 --output "docs/release-coverage/scheduled/$(date +%F)"
