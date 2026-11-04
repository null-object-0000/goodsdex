"""Read actual online responses and compare against the locked published artifact."""
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from goodsdex.source_urls import coverage
root=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--public',type=Path,required=True);a=ap.parse_args()
base='https://spend.snewbie.site'
def fetch(path):
    return subprocess.check_output(['curl','--noproxy','*','--compressed','-fsSL','--connect-timeout','10','--max-time','120',base+path])
expected=json.loads((a.public/'goods.json').read_bytes())
meta=json.loads(fetch('/api/meta'));raw=fetch('/api/goods');actual=json.loads(raw)
(root/'online-goods.json.gz').write_bytes(gzip.compress(raw,mtime=0));(root/'online-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
assert actual==expected,'Actual API goods differ from published artifact'
assert meta['source_url_coverage']==coverage(actual)
checks=[]
for key in ('CN:mi_cn:product:25627','CN:mi_cn:product:10000082','CN:mi_cn:product:10050230'):
    row=json.loads(fetch('/api/goods/'+quote(key,safe='')))
    source=next(r for r in actual if r['id']==key)
    assert row==source
    suffix=key.rsplit(':',1)[-1];(root/f'online-detail-{suffix}.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
    # Sample page evidence already proves exact name match; request its URL again for live access.
    time.sleep(2.15)
    code=subprocess.check_output(['curl','--noproxy','*','--compressed','-sSL','--max-time','30','-o','/dev/null','-w','%{http_code}',row['source_url']],text=True)
    assert code=='200'
    checks.append(dict(id=key,name=row['name'],source_url=row['source_url'],http_status=int(code)))
result=dict(all_goods_equal=True,source_url_coverage=coverage(actual),meta_revision=meta.get('revision'),details=checks,goods_sha256=hashlib.sha256(raw).hexdigest())
(root/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
