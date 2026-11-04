#!/usr/bin/env python3
"""Rate-limited official source URL audit; never treats generic HTTP 200 as a match."""
import argparse
import difflib
import gzip
import hashlib
import html
import json
import random
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, parse_qs


def normalize(value):
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', html.unescape(value).lower())


def match_name(row, title, headings):
    # Compare product-scoped title/headings only. Site navigation contains unrelated names.
    expected = normalize(row['name'])
    candidates = [normalize(x) for x in [title, *headings] if x.strip()]
    candidates = [re.sub(r'(立即购买|小米商城|小米官网|中国官网|官方商城).*$', '', x) for x in candidates]
    scores = [difflib.SequenceMatcher(None, expected, x).ratio() for x in candidates]
    score = max(scores, default=0)
    # SKU/model must include a number; "Pro", "iPad", etc. alone are insufficient.
    models = [row.get(k) for k in ('part_number', 'model', 'model_or_part_number', 'series')]
    models += (row.get('lookup_keys') or [])
    keys = [normalize(x) for x in models if isinstance(x, str) and re.search(r'\d', x) and len(normalize(x)) >= 4]
    hit = next((x for x in keys if any(x in c for c in candidates)), None)
    return score, hit


def fetch(url, folder, index):
    body = folder / f'{index:03}.html.gz'
    raw = folder / f'.{index:03}.body'
    start = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(['curl', '--noproxy', '*', '--compressed', '-sSL', '--connect-timeout', '10', '--max-time', '35', '-A', 'Mozilla/5.0', '-o', str(raw), '-w', '%{http_code}\n%{url_effective}', url], capture_output=True, text=True)
    parts = result.stdout.splitlines()
    content = raw.read_bytes() if raw.exists() else b''
    body.write_bytes(gzip.compress(content, mtime=0))
    raw.unlink(missing_ok=True)
    return dict(status=int(parts[0]) if parts else 0, final_url=parts[1] if len(parts)>1 else url,
                requested_at=start, error=result.stderr.strip(), sha256=hashlib.sha256(content).hexdigest(), evidence=str(body)), content.decode('utf-8', errors='replace')


OFFICIAL = {'小米': ('mi.com',), 'Apple': ('apple.com','apple.com.cn'), '大疆': ('dji.com',),
            '富士': ('fujifilm-x.com','fujifilm.com'), '惠普': ('hpstore.cn','hp.com'),
            '比亚迪': ('bydauto.com.cn','byd.com'), '小米汽车': ('xiaomiev.com',)}


def is_official(brand, url):
    host = (urlsplit(url).hostname or '').lower()
    return any(host == domain or host.endswith('.'+domain) for domain in OFFICIAL[brand])


def audit(row, url, folder, index):
    result, text = fetch(url, folder, index)
    title = re.search(r'<title[^>]*>(.*?)</title>', text, re.S|re.I)
    clean = lambda s: html.unescape(re.sub('<[^>]+>', ' ', s)).strip()
    title = clean(title.group(1)) if title else ''
    headings = [clean(x) for x in re.findall(r'<h[12][^>]*>(.*?)</h[12]>', text, re.S|re.I)]
    score, model = match_name(row, title, headings)
    final = urlsplit(result['final_url'])
    home = final.path in ('', '/', '/cn', '/cn/', '/shop', '/shop/')
    official = is_official(row['brand'], url) and is_official(row['brand'], result['final_url'])
    passed = result['status'] == 200 and official and not home and (score >= .6 or bool(model))
    reason = '通过' if passed else ('跳转首页' if home else '推导不成立：内容不匹配' if result['status']==200 else 'HTTP/传输失败')
    if not official:
        reason = '已有非官方链接（保留，不作为官方验证通过）'
    return dict(id=row['id'], brand=row['brand'], name=row['name'], url=url, existing=bool(row.get('source_url')),
                **result, title=title, headings=headings[:12], score=round(score,4), model_hit=model, passed=passed, reason=reason)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('docs/source-url-20261104'));args=ap.parse_args()
    root=args.root; folder=root/'responses';folder.mkdir(exist_ok=True)
    rows=json.loads(gzip.decompress((root/'baseline-goods.json.gz').read_bytes()))
    samples=[]
    for brand in sorted({r['brand'] for r in rows}):
        group=[r for r in rows if r['brand']==brand and (not r.get('source_url') if brand=='小米' else True)]
        picked=random.Random(20261104).sample(group,min(20,len(group)))
        for row in picked:
            url=row.get('source_url') or 'https://www.mi.com/shop/buy/detail?product_id='+row['id'].rsplit(':',1)[-1]
            samples.append((row,url))
    (root/'sample-plan.json').write_text(json.dumps([dict(id=r['id'],name=r['name'],brand=r['brand'],url=u) for r,u in samples],ensure_ascii=False,indent=2)+'\n')
    results=[];last=0
    for i,(row,url) in enumerate(samples):
        time.sleep(max(0,2.15-(time.monotonic()-last))); last=time.monotonic()
        entry=audit(row,url,folder,i);results.append(entry)
        (root/'samples.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
        print(row['brand'],row['name'],entry['status'],entry['title'][:60],entry['score'],entry['reason'],flush=True)

if __name__=='__main__':main()
