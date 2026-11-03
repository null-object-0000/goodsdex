"""Discovery only: full exact names, never a publication list."""
import json,re,unicodedata
from capture import ROOT
rows=json.load(open('/tmp/goodsdex-round3-before.json'))
def norm(s):return re.sub(r'[\s（）()，,、：:™®-]','',unicodedata.normalize('NFKC',s)).lower()
queue=[]
for a in json.load(open(ROOT/'dji-sale-sections.json')):
 if '/page/' in a['url'] or not a['section']:continue
 for r in rows:
  if r.get('brand')!='大疆' or r.get('release'):continue
  n=norm(r['name']);section=norm(a['section'])
  if n in section:
   queue.append(dict(id=r['id'],name=r['name'],date=a['date'][:7],url=a['url'],section=a['section'],file=a['file']))
(ROOT/'dji-exact-discovery.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
for a in queue:print(a['id'],a['name'],a['date'],a['url'].split('/')[-1])
print('queue',len(queue),'unique',len({a['id'] for a in queue}))
