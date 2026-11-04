import json,pathlib,gzip,re
from bs4 import BeautifulSoup
root=pathlib.Path(__file__).resolve().parent;out=[]
for p in (root/'evidence').glob('*.json'):
 r=json.load(open(p));u=r['url']
 if '/newsroom/' not in u or '/archive' in u or u.endswith('.xml') or r['status']!=200:continue
 soup=BeautifulSoup(gzip.open(r['raw_file']).read(),'html.parser');paras=[' '.join(e.get_text(' ',strip=True).split()) for e in soup.select('p,li,div.pagebody-copy')];out.append(dict(url=u,capture=str(p.relative_to(pathlib.Path.cwd())),title=soup.title.get_text() if soup.title else '',paragraphs=paras))
(root/'apple-paragraphs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
