"""Current Atour/BYD identity-only research; abstentions are not candidates."""
import concurrent.futures,gzip,json,time
from pathlib import Path
import propose_release_l7 as base
OUT=Path('docs/release-coverage/L7-gap')
base.ROOT=OUT/'identity';base.ROOT.mkdir(exist_ok=True)
base.PROMPT=base.PROMPT.replace('；亚朵亦可官方公众号','；禁止公众号、贴吧、短视频、二手和非官方电商。允许官方首发博客公告；官方商城存档必须显示首发/上市。所有季节、尺寸、颜色、套装须有本身证据，不能用家族日期')
rows=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()))
targets=[{k:r.get(k) for k in ('id','name','brand','category')} for r in rows if r['brand'] in ('亚朵星球','比亚迪')]
(OUT/'identity-targets.json').write_text(json.dumps(targets,ensure_ascii=False,indent=2))
for i in range(0,len(targets),50):
 chunk=targets[i:i+50]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(base.work,[chunk[j:j+10] for j in range(0,len(chunk),10)]))
 print('identity batch',i//50+1,len(chunk),flush=True);time.sleep(5)
