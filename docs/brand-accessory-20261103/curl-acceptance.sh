#!/usr/bin/env bash
set -euo pipefail
set -x
curl --noproxy '*' --compressed --connect-timeout 10 --max-time 30 -fsS 'https://spend.snewbie.site/api/meta' | jq '{count,brands,xiaomi_index_count:.files["index/mi_cn.json"].count,unknown_index_count:.files["index/other.json"].count}'
curl --noproxy '*' --compressed --connect-timeout 10 --max-time 30 -fsSG 'https://spend.snewbie.site/api/goods/search' --data-urlencode 'brand=小米' --data-urlencode 'limit=1' | jq '{total,productTotal,facets_version}'
curl --noproxy '*' --compressed --connect-timeout 10 --max-time 30 -fsSG 'https://spend.snewbie.site/api/goods/search' --data-urlencode 'brand=小米' --data-urlencode 'limit=1' --data-urlencode 'facets_version=1' | jq '{total,productTotal,facets_version}'
