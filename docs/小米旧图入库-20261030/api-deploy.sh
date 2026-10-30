#!/usr/bin/env bash
set -euo pipefail
cd /root/spendgood-api
printf '%s\n' 'eaf4b518ccbb6c4fa5d84e09070a99631752794bbd0aca61914ab2f89437a9e6  src/goods.mjs' | sha256sum -c -
backup=$(mktemp -d /tmp/xiaomi-image-api-rollback.XXXXXX)
tar czf "$backup/module.tar.gz" src/goods.mjs
docker tag "$(docker inspect --format='{{.Image}}' spendgood-api)" spendgood-api:xiaomi-image-rollback-20261030
rollback(){ tar xzf "$backup/module.tar.gz"; docker tag spendgood-api:xiaomi-image-rollback-20261030 spendgood-api:local; docker compose up -d --no-build --force-recreate; }
trap 'rc=$?; if [ "$rc" -ne 0 ]; then rollback; fi; exit "$rc"' EXIT
tar xzf /tmp/xiaomi-image-api.tar.gz
sha256sum src/goods.mjs
docker compose build api
docker compose up -d --no-build --force-recreate
curl --retry 12 --retry-delay 2 --retry-all-errors -fsS http://127.0.0.1:8080/healthz
printf '\nbackup=%s\n' "$backup"
