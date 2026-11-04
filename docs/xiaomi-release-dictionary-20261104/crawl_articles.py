from crawl import capture,OUT,ROOT
import json,re,html
items=json.loads((OUT/'newsroom-index.json').read_text())
selected=[]
for a in items:
 title=a['title']
 if 'POCO' in title:continue
 if not re.search('unveil|introduc|launch|announc|revenue|reports|profit|flagship|redmi|AIoT|annual|infinity',title,re.I):continue
 selected.append(a)
(OUT/'selected-articles.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
for a in selected:
 c=capture('https://go.buy.mi.com/global/discovery/land?from=pc&id='+a['metadata']['material_id'])
 if c.get('error'):continue
 p=ROOT/c['capture_file'];data=json.loads(p.read_bytes())
 # Keep original API bytes and separately extract the public body.
 body=json.dumps(data.get('data'),ensure_ascii=False)
 p.with_suffix('.txt').write_text(re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',body))))
