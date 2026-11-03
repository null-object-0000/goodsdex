#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
curl --noproxy '*' --compressed --connect-timeout 10 --max-time 45 -fsS \
  https://spend.snewbie.site/api/meta -o api-meta-after.json
jq '{count,brands,total_all,total_published,total_excluded,revision}' api-meta-after.json
curl --noproxy '*' --compressed --connect-timeout 10 --max-time 45 -fsSG \
  https://spend.snewbie.site/api/goods/search \
  --data-urlencode 'brand=小米' --data-urlencode 'limit=1' -o api-search-after.json
jq '{total,productTotal,facets_version}' api-search-after.json
curl --noproxy '*' --compressed --connect-timeout 10 --max-time 45 -fsSG \
  https://spend.snewbie.site/api/goods/search \
  --data-urlencode 'brand=小米' --data-urlencode 'limit=1' \
  --data-urlencode 'facets_version=1' -o api-search-v1-after.json
jq '{total,productTotal,facets_version}' api-search-v1-after.json
