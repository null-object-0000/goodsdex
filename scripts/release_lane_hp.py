#!/usr/bin/env python3
"""L1: inspect exact-SKU HP support responses, never web publication metadata.

The public devices endpoint is batched only for transport. A response must contain
an exact productNumber before a product release field is considered. Absence of a
release field on this endpoint is NOT evidence that HP has no release information.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import time
import requests

ENDPOINT = 'https://support.hp.com/wcc-services/profile/devices/warranty/specs?cache=true'
WEB_FIELDS = ('webFirstPublishingDate', 'webReleaseDate')
# Only semantically explicit product fields qualify. The observed endpoint has none.
PRODUCT_FIELDS = ('productReleaseDate', 'productLaunchDate', 'productAnnouncementDate')
ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    path = Path(path)
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as f:
        return json.load(f)


def inspect(row, capture):
    result = {'id': row['id'], 'part_number': row.get('part_number'), 'release': None,
              'missing_reason': 'not_collected', 'none_reason': 'obtainable_not_collected'}
    if not row.get('part_number'):
        return dict(result, missing_reason='model_mismatch', detail='No exact orderable part number on family record')
    if capture is None:
        return dict(result, detail='No exact-SKU support response captured')
    result['evidence'] = {k: capture.get(k) for k in ('url','observed_at','status','sha256')}
    if capture.get('status') == 404:
        return dict(result, missing_reason='http_404')
    if capture.get('status') != 200:
        return dict(result, missing_reason='access_failed', detail=f"HTTP {capture.get('status')}")
    try:
        data = json.loads(capture['body'])
        devices = data.get('data', {}).get('devices', []) if data.get('data') else []
        specs = next((d.get('productSpecs', {}).get('data', {}) for d in devices
                      if d.get('productSpecs', {}).get('data', {}).get('productNumber') == row['part_number']), None)
    except (ValueError, TypeError, AttributeError):
        return dict(result, missing_reason='parse_failed')
    if not specs:
        if data.get('code') in (403,406,429):
            return dict(result, missing_reason='access_failed', detail=f"HP application code {data['code']}: {data.get('message')}")
        return dict(result, missing_reason='model_mismatch', detail='No exact productNumber in response')
    result['observed_web_metadata'] = {k: specs[k] for k in WEB_FIELDS if specs.get(k)}
    result['support_product_name'] = specs.get('productName')
    for key in PRODUCT_FIELDS:
        value = str(specs.get(key) or '')
        m = re.fullmatch(r'(\d{4})[-/]?(0[1-9]|1[0-2])(?:[-/]?(0[1-9]|[12]\d|3[01]))?(?:T.*)?', value)
        if not m:
            continue
        date = '-'.join(p for p in m.groups() if p)
        try:
            datetime.strptime(date, '%Y-%m-%d' if m[3] else '%Y-%m')
        except ValueError:
            continue
        result['release'] = {'date': date, 'granularity': 'day' if m[3] else 'month',
            'source': 'official', 'confidence': 'high', 'event': 'announcement' if 'Announcement' in key else 'availability',
            'evidence': dict(result['evidence'], captured_at=capture.get('observed_at'), source_type='official', locator=f'productSpecs.data.{key}',
                             quote=json.dumps({key: specs[key], 'productNumber': specs['productNumber']}, ensure_ascii=False))}
        result['missing_reason'] = None
        return result
    return dict(result, missing_reason='no_release_field', detail='Exact-SKU response has no explicit product release/launch/announcement field. webFirstPublishingDate/webReleaseDate rejected: web metadata without product-event semantics. Does not establish official absence.')


def run(goods, output=ROOT/'docs/release-coverage/l1-hp', *, live=True, cache_paths=(), batch_size=20):
    rows = [r for r in goods if r.get('source') == 'hp_cn' or r.get('id','').startswith('CN:hp_cn:')]
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    cache = {}
    for path in cache_paths:
        if not Path(path).exists():
            continue
        records = read_json(path)
        for record in records if isinstance(records, list) else [records]:
            if not record.get('body') or record.get('sha256') != hashlib.sha256(record['body'].encode()).hexdigest():
                continue
            for d in record.get('payload', {}).get('devices', []):
                if d.get('productNumber'):
                    cache[d['productNumber']] = record
    network = []; current = {}
    candidates = [r for r in rows if r.get('part_number')]
    if live:
        session = requests.Session()
        session.headers['User-Agent'] = 'GoodsDex release-date evidence collector/1.0'
        for offset in range(0, len(candidates), batch_size):
            batch = candidates[offset:offset+batch_size]
            payload = {'cc':'cn','lc':'zh','utcOffset':'P0800','devices':[
                {'seriesOid':None,'modelOid':None,'serialNumber':None,'productNumber':r['part_number'],
                 'displayProductNumber':None,'countryOfPurchase':'cn'} for r in batch]}
            capture = {'url': ENDPOINT, 'method':'POST', 'payload':payload,
                       'observed_at':datetime.now(timezone.utc).isoformat()}
            try:
                response = session.post(ENDPOINT, json=payload, timeout=25)
                capture.update(status=response.status_code, body=response.text,
                    sha256=hashlib.sha256(response.content).hexdigest())
            except requests.RequestException as exc:
                capture.update(status=None, body='', error=str(exc))
            network.append(capture)
            for row in batch:
                current[row['part_number']] = capture
            print(f'L1 requested {min(offset+batch_size,len(candidates))}/{len(candidates)} HTTP {capture.get("status")}', flush=True)
            time.sleep(2.1)
    results = []
    for row in rows:
        sku = row.get('part_number')
        latest = inspect(row, current.get(sku)) if sku in current else None
        historical = inspect(row, cache.get(sku))
        # Preserve diagnostics from independently hash-verifiable existing captures.
        # Never label a blocked request "no field" unless a real exact-SKU body exists.
        result = historical if historical['missing_reason'] == 'no_release_field' else latest or historical
        if latest:
            result['latest_attempt'] = {'missing_reason':latest['missing_reason'], 'evidence':latest.get('evidence'), 'detail':latest.get('detail')}
        results.append(result)
    captured_at = datetime.now(timezone.utc).isoformat()
    observations = [{'id':r['id'], 'reason':r['missing_reason'] or 'hit',
                     'url':r.get('evidence',{}).get('url', ENDPOINT),
                     'none_reason':r.get('none_reason'), 'detail':r.get('detail'),
                     'latest_attempt':r.get('latest_attempt')} for r in results]
    candidates = [{'family':r['id'], 'ids':[r['id']], 'brand':'惠普',
                   'method':'explicit_support_product_release', 'release':r['release']}
                  for r in results if r['release']]
    summary = {'lane':'L1','captured_at':captured_at,'observed_at':captured_at,'total':len(rows),
               'candidates':candidates,'observations':observations,
               'hits':sum(bool(r['release']) for r in results),
               'reasons':dict(Counter(r['missing_reason'] or 'hit' for r in results)),
               'latest_attempt_reasons':dict(Counter(r.get('latest_attempt',{}).get('missing_reason','not_attempted') or 'hit' for r in results)),
               'official_absence_count':0,
               'policy':'No web publication metadata is a product release date; no field on one endpoint is not official absence.',
               'records':results}
    summary['summary'] = {k:summary[k] for k in ('total','hits','reasons','latest_attempt_reasons','official_absence_count')}
    with gzip.open(output/'network.json.gz','wt') as f: json.dump(network,f,ensure_ascii=False)
    (output/'results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--goods', type=Path, required=True)
    p.add_argument('--output',type=Path,default=ROOT/'docs/release-coverage/l1-hp')
    p.add_argument('--offline',action='store_true')
    p.add_argument('--cache',type=Path,action='append',default=[])
    args=p.parse_args()
    result=run(read_json(args.goods),args.output,live=not args.offline,cache_paths=args.cache)
    print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False))

if __name__=='__main__':main()
