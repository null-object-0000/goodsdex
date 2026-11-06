#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="${GOODSDEX_REPO_DIR:-/home/nichangen/代码/self-code/goodsdex}"
STATE_DIR="${GOODSDEX_WATCHDOG_STATE:-/home/nichangen/.hermes/profiles/spendpoint/state/goodsdex-watchdog}"
mkdir -p "$STATE_DIR"
cd "$REPO_DIR"
PYTHONPATH=src:scripts python3 scripts/source_watchdog.py --registry data/official/sources-registry.json --state "$STATE_DIR/leases.json" "$@" 2>&1 | tee -a "$STATE_DIR/watchdog.log"
