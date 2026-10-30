#!/usr/bin/env bash
set -euo pipefail
cd /root/spendgood-api
printf '%s\n' '7760276341af14d56031b4d9d0a028379d3c1402fe044389dc185c35252f7047  src/goods.mjs' '12144ce01cafad026c4028b68fc8e300d51a35ae116a3376e31bb8ec26237b81  src/product-presentation.mjs' | sha256sum -c -
backup=$(mktemp -d /tmp/backfill-api-rollback.XXXXXX)
tar czf "$backup/modules.tar.gz" src/goods.mjs src/product-presentation.mjs
docker tag "$(docker inspect --format='{{.Image}}' spendgood-api)" spendgood-api:backfill-rollback-20261030
rollback(){ tar xzf "$backup/modules.tar.gz"; docker tag spendgood-api:backfill-rollback-20261030 spendgood-api:local; docker compose up -d --no-build --force-recreate; }
trap 'rc=$?; if [ "$rc" -ne 0 ]; then rollback; fi; exit "$rc"' EXIT
tar xzf /tmp/backfill-api.tar.gz
sha256sum src/goods.mjs src/product-presentation.mjs
docker compose build api
docker compose up -d --no-build --force-recreate
curl --retry 12 --retry-delay 2 --retry-all-errors -fsS http://127.0.0.1:8080/healthz
printf 'backup=%s\n' "$backup"
