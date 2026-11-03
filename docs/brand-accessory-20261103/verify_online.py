"""Real curl acceptance, with raw responses retained alongside the summary."""
import concurrent.futures
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.parse

OUT = Path(__file__).resolve().parent
BASE = 'https://spend.snewbie.site'
ROUTES = {
    'api-meta-after.json': '/api/meta',
    'api-search-after.json': '/api/goods/search?' + urllib.parse.urlencode({'brand':'小米', 'limit':1}),
    'api-search-v1-after.json': '/api/goods/search?' + urllib.parse.urlencode({'brand':'小米', 'limit':1, 'facets_version':1}),
    'api-goods-after.json.gz': '/api/goods',
}


def fetch(pair):
    name, route = pair
    raw = subprocess.check_output(['curl', '--noproxy', '*', '--compressed', '--connect-timeout', '10', '--max-time', '180', '-fsS', BASE + route])
    (OUT / name).write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)
    return name, (json.loads(raw), hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        responses = dict(pool.map(fetch, ROUTES.items()))
    meta = responses['api-meta-after.json'][0]
    goods, sha = responses['api-goods-after.json.gz']
    search = responses['api-search-after.json'][0]
    v1 = responses['api-search-v1-after.json'][0]
    assert meta['count'] == len(goods) == 2898
    assert meta['brands']['小米'] == 1684
    assert meta['files']['index/mi_cn.json']['count'] == 1684
    assert meta['files']['index/other.json']['count'] == 0
    assert sum(not r.get('brand') for r in goods) == 0
    assert all(r.get('brand_source') == 'id_prefix' for r in goods)
    assert meta['files']['goods.json']['sha256'] == sha
    removed = json.loads((OUT / 'comparison.json').read_text())['new_exclusions']
    assert not {r['id'] for r in removed} & {r['id'] for r in goods}
    # Full detail, not the listing: brand_source must survive lazy hydration.
    checks = []
    for key, expected in [('CN:mi_cn:product:10000292', 404),
                          ('CN:mi_cn:product:13929', 404),
                          ('CN:mi_cn:product:16549', 200)]:
        route = '/api/goods/' + urllib.parse.quote(key, safe='')
        p = subprocess.run(['curl', '--noproxy', '*', '--connect-timeout', '10', '--max-time', '30', '-sS', '-w', '\n%{http_code}', BASE+route], capture_output=True, check=True)
        body, status = p.stdout.rsplit(b'\n', 1)
        assert int(status) == expected, (key, status)
        if expected == 200:
            detail = json.loads(body)
            # API responds with the full record directly.
            assert detail['brand'] == '小米' and detail['brand_source'] == 'id_prefix'
        checks.append(dict(id=key, status=int(status)))
    result = dict(checked_at=datetime.now(timezone.utc).isoformat(), count=meta['count'],
                  brands=meta['brands'], xiaomi_index_count=meta['files']['index/mi_cn.json']['count'],
                  unknown_count=0, unknown_ratio=0, xiaomi_search_default=search['total'],
                  xiaomi_search_v1=v1['total'], xiaomi_facet=next(x['count'] for x in search['facets']['brands'] if x['value']=='小米'),
                  goods_sha256=sha, goods_matches_manifest=True, detail_checks=checks)
    (OUT / 'online-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
