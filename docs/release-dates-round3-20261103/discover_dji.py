"""Bounded official archive pass: 40 index pages; at most 90 product announcements."""
import json,re,gzip
from capture import ROOT,many
urls=['https://www.dji.com/cn/media-center/announcements/page/'+str(i) for i in range(2,41)]
urls.insert(0,'https://www.dji.com/cn/media-center/announcements')
entries={}
for o in many(urls):
 if o['http_status']!=200:continue
 h=gzip.decompress((ROOT/'evidence'/o['raw_file']).read_bytes()).decode('utf-8','replace')
 m=re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',h,re.S)
 if not m:continue
 d=json.loads(m[1])
 for c in d['props']['initialState']['page']['data']['components_data']:
  listing=c['data'].get('mediaListingData',{}).get('data',{})
  for a in listing.get('news_reports',[]):entries[a['slug']]={k:a.get(k) for k in ['slug','title','published_at','category','tags','excerpt']}
selected=[a for a in entries.values() if a['published_at']>='2023' and ('产品发布' in a['tags'] or re.search('发布|推出|上市|发售',a['title']))]
assert len(selected)<=90,len(selected)
(ROOT/'dji-archive-discovery.json').write_text(json.dumps(dict(index_pages=40,entries=list(entries.values()),selected=selected),ensure_ascii=False,indent=2)+'\n')
print('archive',len(entries),'selected',len(selected),flush=True)
for a in selected:print(a['published_at'],a['slug'],a['title'],flush=True)
for o in many(['https://www.dji.com/cn/media-center/announcements/'+a['slug'] for a in selected]):print('capture',o['url'],o['http_status'],o['bytes'],flush=True)
