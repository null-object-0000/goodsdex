import sys,json,pathlib,re
sys.path.insert(0,'docs/release-dates-round10-20261104');from collect import many
root=pathlib.Path('docs/release-dates-round10-20261104');urls=[]
for cat,n in [('iphone',35),('ipad',23),('mac',26),('apple-watch',12),('airpods',5),('homepod',3),('apple-vision-pro',3)]:urls += [f'https://www.apple.com/newsroom/archive/{cat}/?page={i}' for i in range(1,n+1)]
many(urls)
urls=[]
for p in (root/'evidence').glob('*.json'):
 r=json.load(open(p))
 if 'apple.com/newsroom/archive/' in r['url'] and r['status']==200:
  urls += [x['url'] for x in r['links'] if re.search(r'/newsroom/(200\d|201[0-6])/',x['url']) and re.search(r'iPhone|iPad|MacBook|iMac|Mac-mini|Mac-Pro|Apple-Watch|Cinema-Display|HomePod|AirPods',x['url'],re.I) and not re.search('sales|sale-|results|earnings|million|billion|record|developer|software|beta|sdk|preview|app-|weekend|donate|leopard|lion|safari|ios-|os-x-|AppleCare',x['url'],re.I)]
urls=sorted(set(urls));print('Articles',len(urls),flush=True);(root/'apple-archive-urls.json').write_text(json.dumps(urls,indent=2));many(urls)
