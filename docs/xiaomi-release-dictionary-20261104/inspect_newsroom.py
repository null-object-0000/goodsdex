from pathlib import Path
from html import unescape
import re,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
records=[json.loads(l) for l in (OUT/'fetches.jsonl').read_text().splitlines()]
articles=[]
for c in records:
 if '/discovery/land?' not in c['url'] or c.get('error'):continue
 d=json.loads((ROOT/c['capture_file']).read_bytes()).get('data') or {}
 raw=d.get('content','');text=re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>',' ',raw))).strip()
 def plain(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>',' ',s))).strip()
 headings=[plain(s) for s in re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>',raw,re.S)]
 if not headings:headings=[plain(s) for s in re.findall(r'<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>',raw,re.S) if re.match('(?:Xiaomi|Redmi|REDMI|Mi |MIJIA)',plain(s))]
 articles.append(dict(id=d.get('id'),title=d.get('title'),opening=text[:600],headings=headings,text=text,capture=c))
(OUT/'articles.json').write_text(json.dumps(articles,ensure_ascii=False,indent=2)+'\n')
for a in articles:
 # Print only China launch/earnings records; global retained separately.
 if re.search('mainland|RMB|revenue|profit',a['text'],re.I):
  print(a['id'],a['title']);print(a['opening'][:380]);print('HEADINGS',a['headings'])
  if re.search('revenue|reports',a['title'],re.I):
   print('LAUNCH',re.findall(r'.{0,50}(?:launched|unveiled|released|introduced).{0,180}',a['text'])[:18])
