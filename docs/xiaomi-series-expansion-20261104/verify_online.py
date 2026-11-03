"""Read the actual live catalogue and the existing search hydration API."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import random
import requests
from urllib.parse import quote

OUT=Path(__file__).parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--expected',type=Path,required=True);a=p.parse_args()
    raw=a.expected.read_bytes()
    if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
    expected=json.loads(raw)
    s=requests.Session();s.trust_env=False
    def get(path,**kwargs):
        r=s.get('https://spend.snewbie.site'+path,timeout=45,headers={'Cache-Control':'no-cache'},**kwargs)
        r.raise_for_status();return r,r.json()
    response,rows=get('/api/goods')
    _,meta=get('/api/meta')
    # Check all managed fields, including every legacy internal-only decision.
    projection=lambda rs:[(r['id'],r.get('release'),r.get('release_series')) for r in rs]
    matching=projection(rows)==projection(expected)
    attempt=dict(checked_at=datetime.now(timezone.utc).isoformat(),count=len(rows),
        release_projection_equal=matching, full_catalog_equal=rows==expected,
        sha256=hashlib.sha256(response.content).hexdigest(),revision=meta.get('revision'))
    (OUT/'online-attempts.jsonl').open('a').write(json.dumps(attempt,ensure_ascii=False)+'\n')
    assert matching,'Live API has not synchronized the reviewed release'
    (OUT/'online-goods.json.gz').write_bytes(gzip.compress(response.content,mtime=0))
    (OUT/'online-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    # Random sample is frozen before the request, with no substitution by nicer results.
    ids=sorted({m['id'] for b in json.loads((OUT/'reviewed-new-batches.json').read_text()) for m in b['members']})
    selected=random.Random(20261104).sample(ids,5)
    basic,basic_body=get('/api/goods/search',params={'brand':'小米','limit':5})
    (OUT/'search-basic-after.json').write_bytes(basic.content)
    hydrated,body=get('/api/goods/search',params={'brand':'小米','ids':','.join(selected)})
    (OUT/'search-five-after.json').write_bytes(hydrated.content)
    assert {r['id'] for r in body['items']}==set(selected)
    byid={r['id']:r for r in expected}
    for row in body['items']:
        assert row['release_series']==byid[row['id']]['release_series']
        assert row['release_series']['display_allowed'] is True
        assert row['release_series']['crosscheck_status'] in ('official','corroborated')
        _,detail=get('/api/goods/'+quote(row['id'],safe=''))
        assert detail['release_series']==row['release_series']
    attempt.update(search_url=hydrated.url,search_sample_seed=20261104,search_ids=selected,
                   search_date_objects_match=True,detail_date_objects_match=True)
    (OUT/'online-verification.json').write_text(json.dumps(attempt,ensure_ascii=False,indent=2)+'\n')
    lines=['# 线上 search 的五条真实返回','','固定种子20261104，从本轮53个不同ID抽取5条。基础search沿用轻索引；已有 `ids` 参数负责补全详情，未修改接口或字段语义。完整原响应见 search-five-after.json。','',
           '请求：`'+hydrated.url+'`','','以下只省略无关字段，日期对象来自同一次真实search响应：','','```json']
    lines.append(json.dumps([dict(id=r['id'],name=r['name'],release_series={k:r['release_series'][k] for k in
        ('date','granularity','source','level','event','display','crosscheck_status','display_allowed')}) for r in body['items']],ensure_ascii=False,indent=2))
    lines+=['```','']
    (OUT/'online-five.md').write_text('\n'.join(lines))
    print(json.dumps(attempt,ensure_ascii=False))

if __name__=='__main__':main()
