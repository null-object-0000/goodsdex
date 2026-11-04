from pathlib import Path
import json,re,hashlib,datetime,gzip
p=Path(__file__).parent
files=[p/'responses'/f'fetch-sitemap{i}.raw' for i in (1,2,3)]
links=[];proof=[]
for i,f in enumerate(files,1):
 raw=f.read_bytes() if f.exists() else gzip.decompress(Path(str(f)+'.gz').read_bytes());text=raw.decode();assert '<urlset' in text and '</urlset>' in text
 urls=re.findall(r'<loc>(.*?)</loc>',text);assert len(urls)>100
 links+=urls;proof.append(dict(url=f'https://www.hpstore.cn/sitemap-1-{i}.xml',status=200,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),url_count=len(urls)))
skus=sorted({m[1].upper() for u in links if (m:=re.search(r'^https://www.hpstore.cn/[^/?]+-([a-z0-9]{5}(?:pc|pa))\.html$',u))})
base=json.loads((p/'baseline-hp.json').read_text());active=[r for r in base if r.get('sale_status')!='delisted'];overlap=sum(r.get('part_number') in skus for r in active);assert overlap/len(active)>.95
stamp=json.loads((p/'catalogue.json').read_text())['observed_at'] if (p/'catalogue.json').exists() else datetime.datetime.fromtimestamp(max(f.stat().st_mtime for f in files),datetime.timezone.utc).isoformat()
x=dict(capture_id=hashlib.sha256(json.dumps(proof,sort_keys=True).encode()).hexdigest(),observed_at=stamp,urls=[r['url'] for r in proof],requests=proof,part_numbers=skus,url_count=len(set(links)),prior_active_present=overlap,prior_active_total=len(active))
(p/'catalogue.json').write_text(json.dumps(x,ensure_ascii=False,indent=1)+'\n');print(len(skus),overlap,len(active))
