"""Bounded 50-identity batches; raw LLM output is never publication authority."""
import concurrent.futures
import gzip
import json
from pathlib import Path
import subprocess
import time
import propose_release_l7 as base
from goodsdex.release_coverage import effective, matrix

OUT=Path('docs/release-coverage/L7-scale')
def main():
 OUT.mkdir(exist_ok=True)
 snapshot=OUT/'baseline.json.gz'
 if not snapshot.exists():
  snapshot.write_bytes(gzip.compress(subprocess.check_output(['git','show','origin/data:public/goods.json']),mtime=0))
 rows=json.loads(gzip.decompress(snapshot.read_bytes()))
 print(matrix(rows)['total'],flush=True)
 missing=list({r['id']:r for r in rows if r.get('brand') in ('小米','亚朵星球','比亚迪') and not effective(r)}.values())
 # Interleave 100 exact Atour SKUs with Xiaomi; no date or family expansion inputs.
 groups={b:[{k:r.get(k) for k in ('id','name','brand','category')} for r in missing if r['brand']==b] for b in ('小米','亚朵星球','比亚迪')}
 targets=groups['小米'][:300]+groups['亚朵星球'][:100]+groups['比亚迪']+groups['小米'][300:]
 (OUT/'targets.json').write_text(json.dumps(targets,ensure_ascii=False,indent=2))
 base.ROOT=OUT
 base.PROMPT=base.PROMPT.replace('；亚朵亦可官方公众号','。禁止公众号、贴吧、短视频、二手、非官方电商。允许小米社区/官方博客首发公告以及标明首发/上市的官方商城存档')
 for i in range(0,len(targets),50):
  chunk=targets[i:i+50]
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
   list(pool.map(base.work,[chunk[j:j+10] for j in range(0,len(chunk),10)]))
  print('batch',i//50+1,'identities',len(chunk),'done',flush=True)
  time.sleep(5)
if __name__=='__main__':main()
