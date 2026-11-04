"""Capture only public manufacturer pages; retain raw bytes, hashes and failures."""
import concurrent.futures,datetime,gzip,hashlib,json,pathlib,re,subprocess
from urllib.parse import urljoin,urlparse
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parent

def fetch(url):
 assert any(urlparse(url).hostname==d or urlparse(url).hostname.endswith('.'+d) for d in ('mi.com','apple.com','apple.com.cn','fujifilm.com','fujifilm.com.cn','fujifilm-x.com','dji.com'))
 key=hashlib.sha256(url.encode()).hexdigest()[:20];p=ROOT/'evidence'/key;p.parent.mkdir(exist_ok=True)
 if p.with_suffix('.json').exists():return json.loads(p.with_suffix('.json').read_text())
 t=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(['curl','-L','-sS','--compressed','--max-time','35','-w','\n%{http_code}',url],capture_output=True)
 body,_,status=r.stdout.rpartition(b'\n');soup=BeautifulSoup(body,'html.parser');enc=soup.original_encoding or 'utf-8'
 if 'mall-jp' in url: soup=BeautifulSoup(body.decode('shift_jis',errors='replace'),'html.parser')
 links=[{'url':urljoin(url,a['href']),'text':a.get_text(' ',strip=True)} for a in soup.select('a[href]')]
 for tag in soup(['script','style','nav','footer','header']):tag.decompose()
 txt=soup.get_text('\n',strip=True)
 p.with_suffix('.html.gz').write_bytes(gzip.compress(body));p.with_suffix('.txt').write_text(txt)
 out=dict(url=url,status=int(status or 0),curl_exit=r.returncode,error=r.stderr.decode(errors='replace')[:400],sha256=hashlib.sha256(body).hexdigest(),captured_at=t,encoding=enc,links=links,text_file=str(p.with_suffix('.txt').relative_to(pathlib.Path.cwd())),raw_file=str(p.with_suffix('.html.gz').relative_to(pathlib.Path.cwd())))
 p.with_suffix('.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out

def many(urls):
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:return list(ex.map(fetch,dict.fromkeys(urls)))
if __name__=='__main__':
 import sys
 for r in many(sys.argv[1:]): print(r['status'],r['url'],r['text_file'])
