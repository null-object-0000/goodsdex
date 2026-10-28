"""Public, cached automotive source capture. Staging only; never publishes unverified rows.

PYTHONPATH=src:scripts python scripts/car_catalog.py --out data/car-pilot
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlsplit
from urllib.request import urlopen, Request
from datetime import datetime, timezone

BYD = 'https://cms-api.byd.com/car/byd/cn/'
# Explicit pilot scope; IDs are observed official goods IDs, not inferred model years.
PILOT = ('131', '144', '165', '154', '159', '151', '10050', '10030')

class Capture:
    """One serialized session, persistent per-host pacing, hard request budget."""
    def __init__(self, out, max_requests=120):
        self.out = Path(out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.requests = 0
        self.max_requests = max_requests

    def get(self, url, data=None, headers=None):
        import fcntl
        key = hashlib.sha256(url.encode() + (data or b'')).hexdigest()
        target = self.out / (key + '.body')
        if not target.exists():
            if self.requests >= self.max_requests:
                raise ValueError('Car HTTP request budget exhausted')
            host = urlsplit(url).netloc
            # Shared by all local Capture instances/processes; redirects are rejected.
            from urllib.request import build_opener, HTTPRedirectHandler
            class NoRedirect(HTTPRedirectHandler):
                def redirect_request(self, *args, **kwargs):
                    raise ValueError('Unexpected source redirect; review canonical URL')
            with open('/tmp/goodsdex-car-http.lock', 'a+') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                lock.seek(0)
                last = json.loads(lock.read() or '{}')
                time.sleep(max(0, 2.2 - (time.time() - last.get(host, 0))))
                self.requests += 1
                status = None
                try:
                    request = Request(url, data=data, headers=headers or {})
                    with build_opener(NoRedirect).open(request, timeout=40) as response:
                        body = response.read()
                        if body[:2] == b'\x1f\x8b':
                            body = gzip.decompress(body)
                        status = response.status
                finally:
                    last[host] = time.time()
                    lock.seek(0); lock.truncate(); lock.write(json.dumps(last)); lock.flush()
                    (self.out / (key + '.json')).write_text(json.dumps({
                        'url': url, 'method': 'POST' if data is not None else 'GET',
                        'status': status, 'finished_at': datetime.now(timezone.utc).isoformat(),
                        'sha256': hashlib.sha256(body).hexdigest() if status else None,
                    }, ensure_ascii=False, indent=2))
            target.write_bytes(body)
        return target.read_bytes()

    def json(self, url, data=None, headers=None):
        value = json.loads(self.get(url, data, headers))
        if value.get('code') != 0:
            raise ValueError(f'Official API did not succeed: {url}: {value.get("code")}')
        return value['data']


def byd_candidates(info, configs, goods_id):
    """Preserve configuration-level evidence without claiming unverified price semantics."""
    model = info['goodsinfoList']['items'][0]
    rows = []
    for c in configs:
        if c.get('type') != '车型' or not c.get('show_status') or str(c.get('is_presell')) == '1':
            continue
        if not c.get('attrId') or not c.get('name'):
            raise ValueError('Missing official trim identity')
        rows.append({
            'id': f'CN:byd:car:goods-{goods_id}:unknown:attr-{c["attrId"]}',
            'brand': '比亚迪', 'series': model['name'], 'model_year': None,
            'trim': c['name'], 'name': f'比亚迪 {model["name"]} {c["name"]}',
            'kind': 'machine', 'category': '汽车', 'product_type': 'car',
            'price': None, 'price_kind': 'none',
            'price_missing_reason': 'Official configuration amount captured; MSRP semantics require independent verification',
            'official_config_amount': c.get('price'),
            'official_config_price_remark': c.get('priceRemark'),
            'official_promotion_description': c.get('description'),
            'image': c.get('seriesImg') or c.get('icon'),
            'source_url': 'https://www.bydauto.com.cn/cn/parameter-comparison?goodsId=' + goods_id,
            'configuration_source_url': BYD + 'getGoodsAttrListForCompareByGoodsId?goodsId=' + goods_id,
            'params': {}, 'params_missing_reason': 'Official parameter endpoint requires a signature; not bypassed',
            'record_level': 'configuration', 'sale_status': 'official_order_page',
            'review_status': 'staging_only',
        })
    return rows




def verify_byd_parameters(rows, payload):
    """Require exact trim-name and official MSRP row; different order is expected."""
    import re
    if payload.get('code') != 200 or not payload.get('success'):
        raise ValueError('Official parameters failed')
    groups = payload['data']['configs']
    headings = [r for g in groups for r in g['value'] if r['name'] in ('车型', '销售宣传名称')]
    if len(headings) != 1:
        raise ValueError('Ambiguous trim columns')
    titles = headings[0]['value']
    for row in rows:
        if titles.count(row['trim']) != 1:
            raise ValueError('Trim must match exactly: ' + row['trim'])
        index = titles.index(row['trim'])
        params = {}
        for group in groups:
            for cell in group['value']:
                values = cell['value']
                if len(values) == len(titles):
                    params[group['name'] + '/' + cell['name']] = values[index]
                elif len(values) == 1:
                    params[group['name'] + '/' + cell['name']] = values[0]
                else:
                    raise ValueError('Unexplained merged parameter columns')
        prices = [r['value'][index] for g in groups for r in g['value'] if re.fullmatch(r'建议零售价\s*[（(]元[）)]', r['name'])]
        if len(prices) == 1 and re.fullmatch(r'[\d,]+\s*', prices[0]):
            amount = int(prices[0].replace(',', '').strip())
            if amount != row['official_config_amount']:
                raise ValueError('Configuration amount disagrees with MSRP')
            row.update(price=amount, price_kind='msrp', price_label='建议零售价')
            row.pop('price_missing_reason', None)
        row['params'] = params
        row.pop('params_missing_reason', None)
        row['spec_source_url'] = 'https://site-api.byd.com/domestic-official-api/goods/goodsParams?goodsId=' + row['id'].split(':goods-')[1].split(':')[0]
    return rows

def xiaomi_candidates(payload):
    """Join specification columns by SSU ID, never by column order."""
    import re
    if payload.get('code') != 0:
        raise ValueError('Official comparison API failed')
    rows = []
    for table in payload['data']['paramComparisonTableVOList']:
        series = ('SU7 Ultra' if 'Ultra' in table['pdfFileName'] else
                  'YU7' if 'YU7' in table['pdfFileName'] else 'SU7')
        for variant in table['carSsuDataList']:
            ssu = variant['carSsuId']
            params = {}
            for group in table['groups']:
                cols = [c for c in group['paramComparisonCols'] if c['carSsuId'] == ssu]
                if len(cols) != 1:
                    raise ValueError('Missing or duplicate SSU column')
                for cell in cols[0]['paramComparisonCells']:
                    if cell.get('paramName') and cell.get('paramValue'):
                        params[group['groupName'] + '/' + cell['paramName']] = cell['paramValue']
            amount = variant['pcCarVersionPrice']
            if table.get('headerTitle') != '统一零售价' or not re.fullmatch(r'¥\s*[\d,]+', amount):
                raise ValueError('Unrecognized official price basis')
            name = variant['pcCarVersionName']
            year = re.search(r'（(20\d{2})版）', name)
            rows.append({
                'id': f'CN:xiaomi_ev:car:item-{table["carItemId"]}:unknown:ssu-{ssu}',
                'brand': '小米汽车', 'series': series, 'trim': name,
                'model_year': None, 'official_edition': year[0] if year else None,
                'name': '小米汽车 ' + name, 'kind': 'machine', 'category': '汽车',
                'product_type': 'car', 'price': int(re.sub(r'[^0-9]', '', amount)),
                'price_kind': 'msrp', 'price_label': table['headerTitle'],
                'image': table.get('carImg') or None,
                'image_missing_reason': 'Comparison API has no vehicle photograph; wordmark is not used as car image',
                'params': params, 'record_level': 'configuration',
                'source_url': 'https://www.xiaomiev.com/xiaomi/car-config',
                'spec_source_url': table.get('pdfConfigDownloadUrl'),
                'review_status': 'staging_only',
                'sale_status': 'comparison_listed_orderability_unverified',
            })
    return rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    capture = Capture(out / 'captures')
    rows, gaps = [], []
    for goods_id in PILOT:
        try:
            info = capture.json(BYD + 'getGoodsInfoById?goodsId=' + goods_id)
            configs = capture.json(BYD + 'getGoodsAttrListForCompareByGoodsId?goodsId=' + goods_id)
            candidates = byd_candidates(info, configs, goods_id)
            if not candidates:
                raise ValueError('No visible non-presale configurations')
            rows.extend(candidates)
        except Exception as exc:
            gaps.append({'goods_id': goods_id, 'error': str(exc)})
    for filename, obj in [('candidates.json', rows), ('gaps.json', gaps)]:
        (out / filename).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'staged': len(rows), 'gaps': gaps}, ensure_ascii=False))

if __name__ == '__main__':
    main()
