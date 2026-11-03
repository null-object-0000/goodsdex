import sys,re,json,concurrent.futures,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp');from release_probe import get
out=Path('docs/release-dates-20261103/evidence');s=next(json.loads(p.read_text()) for p in out.glob('*.json') if json.loads(p.read_text())['url']=='https://www.apple.com.cn/newsroom/sitemap.xml')
urls=list(dict.fromkeys(re.findall(r'https://www\.apple\.com\.cn/newsroom/(?:201[6-9]|202[01])/\d{2}/[^\s<]+/',s['text'])))
urls=[u for u in urls if re.search('introduc|unveil|launch|announc|new-',u) and re.search('iphone|ipad|macbook|imac|mac-mini|mac-pro|airpods|watch-series|watch-se|homepod|airtag',u) and not re.search('software|music|app-|ios-|ipados|macos|watchos|winners|awards|shot-on|challenge|campaign|store|safari|swift|fund|privacy|features|creativ|students|earth|video|photo',u)]
print('older source pages',len(urls),flush=True)
for o in concurrent.futures.ThreadPoolExecutor(8).map(get,urls[:80]):
 key=hashlib.sha256(o['url'].encode()).hexdigest()[:16];(out/(key+'.json')).write_text(json.dumps(o,ensure_ascii=False,indent=1));print(o['url'],o.get('error',o.get('bytes')),flush=True)
