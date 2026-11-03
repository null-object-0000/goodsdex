"""Complete the 471-entry CN archive, including titles without release keywords."""
import json
from capture import *
entries=json.load(open('docs/release-dates-round3-20261103/dji-archive-discovery.json'))['entries'];out=[]
for a in sorted(entries,key=lambda a:a['published_at'],reverse=True):
 o=get('https://www.dji.com/cn/media-center/announcements/'+a['slug']);out.append(dict(entry=a,capture={k:o.get(k) for k in ['url','http_status','sha256','bytes','evidence_file','error']}));save('dji-complete.json',out)
print('DONE',len(out),flush=True)
