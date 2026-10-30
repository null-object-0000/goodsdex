#!/usr/bin/env bash
set -euo pipefail
cd /root/spendgood-api
printf '%s\n' 'd554e74aea305b337fa9e32db9dd450a812046bc984ad00bd705b6a958e76bff  src/goods.mjs' '2b739069b0828c635dce572884a28c477086d20968b42fe77d2e6a1d0aefdd44  src/product-presentation.mjs' | sha256sum -c -
backup=$(mktemp -d /tmp/car-api-rollback.XXXXXX)
tar czf "$backup/modules.tar.gz" src/goods.mjs src/product-presentation.mjs
docker tag "$(docker inspect --format='{{.Image}}' spendgood-api)" spendgood-api:car-rollback-20261030
rollback(){ tar xzf "$backup/modules.tar.gz"; rm -f src/car-products.mjs; docker tag spendgood-api:car-rollback-20261030 spendgood-api:local; docker compose up -d --no-build --force-recreate; }
trap 'rc=$?; if [ "$rc" -ne 0 ]; then rollback; fi; exit "$rc"' EXIT
tar xzf /tmp/car-api-modules.tar.gz
sha256sum src/goods.mjs src/product-presentation.mjs src/car-products.mjs
docker compose build api
docker compose up -d --no-build --force-recreate
curl --retry 12 --retry-delay 2 --retry-all-errors -fsS http://127.0.0.1:8080/healthz || curl --retry 6 --retry-delay 2 --retry-all-errors -fsS https://spend.snewbie.site/healthz
printf 'backup=%s\n' "$backup"
