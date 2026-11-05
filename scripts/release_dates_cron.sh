#!/usr/bin/env bash
# Independent daily release lane; default L3. flock is held across collection and report writes.
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
export PYTHONPATH="$PWD/src"
exec 9>"/tmp/goodsdex-release-dates.lock"
flock -n 9 || exit 0
PYTHON_BIN="${GOODSDEX_PYTHON:-python3}"
LANE="${GOODSDEX_RELEASE_LANE:-L3}"
case "$LANE" in L1|L2|L3|L4|L5|L6|all) ;; *) echo "Unknown release lane: $LANE" >&2; exit 2 ;; esac
EXTRA=()
if [ "${GOODSDEX_L6_FULL:-0}" = 1 ]; then EXTRA+=(--l6-full); fi
"$PYTHON_BIN" scripts/release_dates_run.py --lane "$LANE" --output "docs/release-coverage/scheduled/$LANE/$(date +%F)" "${EXTRA[@]}"
