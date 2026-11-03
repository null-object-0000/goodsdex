"""GET only; serialize all probes. Record public response headers, never credentials."""
import json, time, hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import os
OUT=Path(os.environ.get('HP_PROBE_OUT', Path(__file__).resolve().parent))
OUT.mkdir(parents=True,exist_ok=True)
URL='https://www.hpstore.cn/hp-omen-16-inch-gaming-laptop-ap1025ax-dc0f0pa.html'
results=[]
def probe(url, mode, ua, delay):
    time.sleep(delay)
    start=datetime.now(timezone.utc).isoformat()
    try:
        try: r=urlopen(Request(url,headers={'User-Agent':ua}),timeout=35)
        except HTTPError as e: r=e
        with r:
            body=r.read()
            headers={k:v for k,v in r.headers.items() if k.lower() in ('server','cf-ray','date','content-type','retry-after') or k.lower().startswith('x-')}
            result=dict(url=url,mode=mode,started_at=start,finished_at=datetime.now(timezone.utc).isoformat(),status=r.code,final_url=r.url,headers=headers,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(), product_marker=b'magentoStorefrontEvents.context.setProduct(' in body, sku_present=b'DC0F0PA' in body)
            (OUT/f'response-{len(results)+1}.txt').write_text(body[:2000].decode(errors='replace'))
    except Exception as e: result=dict(url=url,mode=mode,started_at=start,error=str(e))
    results.append(result)
    (OUT/'probes.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result),flush=True)
for mode,ua,delay in [('browser-ua','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',0),('delay-10s','GoodsDex/1.0 (public computer catalogue; daily)',10),('serial-concurrency-1','GoodsDex/1.0 (public computer catalogue; daily)',2.1)]:
    for _ in range(3): probe(URL,mode,ua,delay)
for url in ['https://www.hp.com.cn/','https://www.hp.com/cn-zh/shop/hp-omen-16-inch-gaming-laptop-ap1025ax-dc0f0pa.html','https://item.jd.com/100149129016.html']:
    probe(url,'alternative','Mozilla/5.0',2.1)
