"""Verify frozen inputs, original fields, OSS bytes, live details and list omission."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'src'))
from goodsdex.date_enrichment import DEFAULT_INPUT, apply_date_enrichment, brand_of, coverage
BASE='https://spend.snewbie.site'
OSS='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public'
FIELDS=('release','release_series','page_first_archived','release_llm')


def get(url):
    return subprocess.check_output(['curl','--compressed','--noproxy','*','-fsS','--retry','2','--max-time','90',url])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--published',type=Path,required=True)
    ap.add_argument('--online',action='store_true')
    a=ap.parse_args()
    raw=a.published.read_bytes();after=json.loads(raw)
    before=json.loads(gzip.decompress((P/'baseline-goods.json.gz').read_bytes()))
    bundle=json.loads(gzip.decompress(DEFAULT_INPUT.read_bytes()))
    assert after==apply_date_enrichment(before)
    assert [{k:v for k,v in r.items() if k not in FIELDS[2:]} for r in after]==before
    counts={f:dict(before=sum(bool(r.get(f)) for r in before),after=sum(bool(r.get(f)) for r in after))for f in FIELDS}
    assert counts['release']==dict(before=671,after=671)
    assert counts['release_series']==dict(before=149,after=149)
    jobs={j['job_id']:j for j in bundle['wayback_manifest']['jobs']}
    statuses={s:sum(r['status']==s for r in bundle['wayback_results'])for s in ('archived','not_archived','error')}
    record_statuses={s:sum(len(jobs[r['id']]['record_ids']) for r in bundle['wayback_results'] if r['status']==s)for s in statuses}
    samples={}
    for field in FIELDS[2:]:
        rows=[r for r in after if r.get(field)]
        # Include coexistence and both nonempty model brands, then stable diverse examples.
        selected=[]
        for group in ([r for r in rows if r.get('release')],*[ [r for r in rows if brand_of(r)==b]for b in sorted({brand_of(r)for r in rows})],rows):
            for row in group:
                if row['id'] not in {r['id']for r in selected}:
                    selected.append(row);break
            if len(selected)==5:break
        for row in rows:
            if len(selected)==5:break
            if row['id'] not in {r['id']for r in selected}:selected.append(row)
        samples[field]=[dict(id=r['id'],name=r['name'],brand=brand_of(r),date=r[field]['date'],
                             evidence_url=r[field].get('evidence_url') or (r[field].get('evidence')or{}).get('url'),
                             release=r.get('release'),release_series=r.get('release_series'),assertion=r[field],
                             api=BASE+'/api/goods/'+quote(r['id'],safe=''))for r in selected]
    report=dict(verified_at=datetime.now(timezone.utc).isoformat(),rows=len(after),counts=counts,
                coverage=coverage(after),original_fields_equal=True,wayback_pages=statuses,wayback_records=record_statuses,
                wayback_published_statuses={s:sum(r['id'] in {key for result in bundle['wayback_results'] if result['status']==s for key in jobs[result['id']]['record_ids']}for r in after)for s in statuses},
                coexists_with_product={f:sum(bool(r.get(f))and bool(r.get('release'))for r in after)for f in FIELDS[2:]},
                samples=samples,brand_accuracy=bundle['llm_accuracy'],goods_sha256=hashlib.sha256(raw).hexdigest())
    if a.online:
        assert get(OSS+'/goods.json')==raw
        oss_meta=json.loads(get(OSS+'/meta.json'));api_meta=json.loads(get(BASE+'/api/meta'))
        assert oss_meta['files']['goods.json']['sha256']==report['goods_sha256']
        assert api_meta['files']['goods.json']['sha256']==report['goods_sha256']
        live=json.loads(get(BASE+'/api/goods'));assert live==after
        live_samples={}
        for field,rows in samples.items():
            live_samples[field]=[]
            for sample in rows:
                payload=json.loads(get(sample['api'])); row=payload.get('item',payload)
                assert row[field]==sample['assertion']
                for f in ('release','release_series'):
                    assert row.get(f)==sample.get(f)
                live_samples[field].append(dict(api=sample['api'],response=row))
        series=next(r for r in after if r.get('release_series'))
        url=BASE+'/api/goods/'+quote(series['id'],safe='');row=json.loads(get(url))
        assert row['release_series']==series['release_series']
        live_samples['release_series']=[dict(api=url,response=row)]
        for query in ('q=Apple&limit=5','q='+quote('小米')+'&limit=5&group_products=1'):
            listing=json.loads(get(BASE+'/api/goods/search?'+query))
            assert listing['items']
            assert all(not any(f in r for f in FIELDS[1:])for r in listing['items'])
        report.update(oss_bytes_equal=True,api_catalog_equal=True,list_omits_detail_dates=True)
        (P/'live-api-samples.json').write_text(json.dumps(live_samples,ensure_ascii=False,indent=2)+'\n')
        (P/'api-meta-after.json').write_text(json.dumps(api_meta,ensure_ascii=False,indent=2)+'\n')
    (P/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines=['# 新字段各五条真实样本','', '日期以 release > release_series > release_llm 为准；页面首存不参与排序。','']
    for field,rows in samples.items():
        lines += ['## '+field,'','|id|名称|日期|证据|与单品日期并存|与系列日期并存|','|---|---|---|---|---|---|']
        for r in rows:
            lines += [f"|{r['id']}|{r['name']}|{r['date']}|[原依据]({r['evidence_url']})|{'是'if r['release']else'否'}|{'是'if r['release_series']else'否'}|"]
        lines+=['']
    (P/'samples.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k not in ('samples','brand_accuracy')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
