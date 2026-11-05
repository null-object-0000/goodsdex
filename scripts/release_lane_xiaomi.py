#!/usr/bin/env python3
"""L3: re-fetch official newsroom/China product paths; never infer from timestamps.

run(rows, output_dir, refresh=True) returns a lane bundle. Publication accepts only
reviewed exact-ID statements; discovery diagnostics never become release dates.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'data/official/xiaomi-priority-release-evidence.json'


def in_scope(row):
    if not row.get('id','').startswith('CN:mi_cn:'):
        return False
    name = row.get('name','')
    if re.search(r'贴纸|贴膜|滤芯|换新服务|悬浮键盘|配件', name):
        return False
    return (row.get('category') in ('笔记本','台式机','显示器','办公娱乐显示器','游戏电竞显示器','键鼠套装','宠物饮水机')
            or bool(re.search(r'笔记本|游戏本|[Bb]ook|鼠标|键鼠|宠物',name)))


def fetch(url, directory, refresh):
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    meta = directory / (key + '.json')
    if not refresh and meta.exists():
        return json.loads(meta.read_text())
    result = dict(url=url, captured_at=datetime.now(timezone.utc).isoformat())
    try:
        response = requests.get(url, timeout=22)
        result.update(status=response.status_code, final_url=response.url,
                      sha256=hashlib.sha256(response.content).hexdigest())
        raw = directory / (key + '.bin')
        raw.write_bytes(response.content)
        result['capture_file'] = str(raw.relative_to(ROOT)) if raw.is_relative_to(ROOT) else str(raw)
        if response.status_code != 200:
            result['reason'] = 'http_' + str(response.status_code)
        elif len(response.content) < 100:
            result['reason'] = 'empty_or_shell_response'
        else:
            result['reason'] = 'retrieved_requires_exact_model_event_review'
    except requests.RequestException as error:
        result.update(reason='transport_error', error=str(error))
    meta.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result


def run(rows, output_dir=None, refresh=True, live=None):
    if live is not None:
        refresh = live
    out = Path(output_dir or ROOT/'docs/release-coverage/l3-xiaomi')
    captures = out/'captures'
    captures.mkdir(parents=True, exist_ok=True)
    selected = {r['id']:r for r in rows if in_scope(r)}
    # Follow the actual article JSON behind the rendered official newsroom page.
    discovery_urls = [
        'https://www.mi.com/about/history',
        'https://go.buy.mi.com/global/page/discovery?from=pc&page_num=1&show_type=newsroom',
        'https://go.buy.mi.com/global/discovery/land?from=pc&id=1668',
        'https://go.buy.mi.com/global/discovery/land?from=pc&id=2722',
        'https://www.mi.com/redmi-monitors/g27q-2025',
        'https://www.mi.com/redmibook/pro14',
        'https://drive.google.com/drive/folders/16J9lT8YIxiLrb2ySSX30JPAvG1miZuf-?usp=sharing',
        'https://blog.mi.com/en/2017/09/11/mi-mix-2-mi-note-3-mi-notebook-pro/',
    ]
    urls = list(dict.fromkeys(discovery_urls + [r.get('source_url') for r in selected.values()
                            if r.get('source_url','').startswith('https://www.mi.com/')]))
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda u:fetch(u,captures,refresh), urls))
    by_url = {r['url']:r for r in results}
    records=[]
    for key,row in selected.items():
        url=row.get('source_url')
        capture=by_url.get(url)
        reason = (capture['reason'] if capture and capture['reason'].startswith(('http_','transport_','empty_'))
                  else 'no_verified_month_level_statement_for_exact_model')
        records.append(dict(id=key,name=row['name'],category=row.get('category'),source_url=url,
                            status='missing',missing_reason='not_obtained',reason=reason,
                            official_absence_confirmed=False,capture=capture))
    # A real primary-source date was found, but its generation is absent from the
    # current catalogue. Keep it as discovery evidence, never copy to 2024/25/26.
    discoveries=[]
    article=by_url[discovery_urls[2]]
    if article.get('status') == 200:
        p=Path(article['capture_file']);p=p if p.is_absolute() else ROOT/p
        try:
            body=json.loads(p.read_bytes())['data']['content']
            text=html.unescape(re.sub('<[^>]+>',' ',body))
            needle='Official sales start from March 4th, 2021 via all Xiaomi official channels in Mainland China.'
            if needle in text and '11th Gen Intel' in text:
                discoveries.append(dict(product='RedmiBook Pro 14/15 2021 Intel H35',date='2021-03-04',
                    granularity='day',event='availability',market='CN',url=article['url'],
                    quote=needle,sha256=article['sha256'],captured_at=article['captured_at'],
                    locator='data.content / RedmiBook Pro section',
                    disposition='not_applied_model_generation_not_in_catalogue'))
        except (ValueError,KeyError,TypeError):pass
    bundle=dict(schema=1,lane='L3',captured_at=datetime.now(timezone.utc).isoformat(),
                scope='priority_categories_all_xiaomi_candidates',total=len(records),
                summary=dict(total=len(records), hits=0, missing=len(records)),
                observations=[dict(id=r['id'],reason=r['reason'],url=r['source_url']) for r in records],
                candidates=[],records=records,captures=results,discoveries=discoveries,
                policy='No page archive, publication metadata, testing report, model-year or overseas launch date is a China release assertion.')
    out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    return bundle


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--goods',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=DEFAULT)
    parser.add_argument('--evidence-dir',type=Path,default=ROOT/'docs/release-coverage/l3-xiaomi')
    parser.add_argument('--reuse-captures',action='store_true')
    args=parser.parse_args()
    bundle=run(json.loads(args.goods.read_text()), args.evidence_dir, not args.reuse_captures)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(lane='L3',total=bundle['total'],hits=len(bundle['candidates']),discoveries=len(bundle['discoveries'])),ensure_ascii=False))


if __name__=='__main__':main()
