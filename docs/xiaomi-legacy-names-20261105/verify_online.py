"""Read-only verification of the real published API and full-library name scan."""
import collections,gzip,json,re,subprocess
from pathlib import Path
from urllib.parse import urlencode
root=Path(__file__).parent
base='https://spend.snewbie.site'

def fetch(path,output):
    result=subprocess.run(['curl','--noproxy','*','--compressed','-fsSL','--connect-timeout','10','--max-time','180',base+path],capture_output=True)
    if result.returncode: raise RuntimeError(result.stderr.decode())
    rows=json.loads(result.stdout)
    output.write_bytes(gzip.compress(result.stdout,mtime=0))
    return rows

if __name__=='__main__':
    query=fetch('/api/goods?'+urlencode({'q':'小米笔记本 Air'}),root/'online-air-response.json.gz')
    rows=fetch('/api/goods',root/'online-goods.json.gz')
    manifest=json.loads(Path('data/official/mi-legacy-names.json').read_text());expected={r['id']:r for r in manifest['items']};actual={r['id']:r for r in rows}
    results=[]
    for key,e in expected.items():
        r=actual[key]
        for field,value in dict(name=e['name'],status='retired',is_historical=True,price=None,price_missing=True,historical_price=e['historical_price']).items():
            assert r.get(field)==value,(key,field,r.get(field),value)
        assert not r.get('release')
        results.append({k:r.get(k) for k in ['id','name','source_url','status','is_historical','price','price_missing','historical_price','release','name_source']})
    qrows=query if isinstance(query,list) else query['items']
    assert {r['id'] for r in qrows} >= {key for key,e in expected.items() if ' Air ' in e['name']}
    pattern=re.compile(r'^\s*(?:\d+(?:\.\d+)?["寸英寸]|第?[一二三四五六七八九十0-9]+代)')
    remaining=[{k:r.get(k) for k in ['id','brand','name']} for r in rows if pattern.match(r.get('name',''))]
    before=json.loads(gzip.decompress((root/'baseline-goods.json.gz').read_bytes()))
    assert {r['id'] for r in before if r['id'] in expected} <= set(actual)
    report=dict(ok=True,total=len(rows),verified_targets=len(results),air_query_count=len(qrows),air_target_count=6,remaining_hits=len(remaining),remaining_by_brand=dict(collections.Counter(r['brand'] for r in remaining)),remaining=remaining,targets=results)
    (root/'online-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=1)+'\n')
    (root/'online-targets.json').write_text(json.dumps([actual[k] for k in expected],ensure_ascii=False,indent=1)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['targets','remaining']},ensure_ascii=False))
