import json,re,unicodedata
from capture import ROOT,save
rows=json.load(open('/tmp/goodsdex-round3-published-goods.json'))
def norm(s):return re.sub(r'[\s（）()，,、：:™®“”"\-]','',unicodedata.normalize('NFKC',s)).lower()
queue=[]
for a in json.load(open(ROOT/'dji-articles.json')):
 o=a['capture'];s=o['text'];end=s.find('探索更多');s=s[:end] if end>=0 else s
 starts=[m.start() for m in re.finditer('售价(?:与|及)|价格(?:与|及)|发售(?:与|及)|售价和',s)]
 section=s[starts[-1]:] if starts else s
 hits=[dict(id=r['id'],name=r['name']) for r in rows if r.get('brand')=='大疆' and not r.get('release') and norm(r['name']) in norm(s)]
 if hits:queue.append(dict(slug=a['entry']['slug'],date=a['entry']['published_at'][:7],hits=hits,section=section))
save('dji-review-queue.json',queue)
for a in queue:print(a['slug'],a['date'],a['hits'],'\n',a['section'][:2200],'\n')
