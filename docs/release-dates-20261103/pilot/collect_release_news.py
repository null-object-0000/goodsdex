import sys,re,json,concurrent.futures,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp');from release_probe import get
out=Path('docs/release-dates-20261103/evidence')
sitemap=next(json.loads(p.read_text()) for p in out.glob('*.json') if json.loads(p.read_text())['url']=='https://www.apple.com.cn/newsroom/sitemap.xml')
urls=re.findall(r'https://www\.apple\.com\.cn/newsroom/\d{4}/\d{2}/[^\s<]+/',sitemap['text'])
urls=list(dict.fromkeys(u for u in urls if re.search(r'/(?:apple-(?:introduces|unveils|announces|updates|launches)|introducing|new-|all-new-|iphone-|homepod-|airpods-|ipad-)',u.split('/newsroom/')[1]) and not re.search('music|tv-plus|arcade|podcast|store|fitness|developer|security|software|ios-|ipados|macos|watchos',u)))
# Limit the pilot: latest model families plus historical models since 2016.
urls=[u for u in urls if int(u.split('/')[4])>=2016]
print('selected',len(urls),flush=True)
# CN sitemap has ~100 suitable model-family announcements, not 640 SKU calls.
urls=urls[:125]
manifest=[]
for o in concurrent.futures.ThreadPoolExecutor(8).map(get,urls):
 key=hashlib.sha256(o['url'].encode()).hexdigest()[:16];(out/(key+'.json')).write_text(json.dumps(o,ensure_ascii=False,indent=1));manifest.append({'key':key,'url':o['url'],'error':o.get('error'),'bytes':o.get('bytes')});print(o['url'],o.get('error',o.get('bytes')),flush=True)
Path('docs/release-dates-20261103/news-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=1))
