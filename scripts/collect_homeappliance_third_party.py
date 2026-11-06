"""Capture reviewed, single-model ZOL parameter pages, explicitly third-party.

No search snippets or series comparison columns are accepted as source values.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from collect_homeappliance_params import request

# Candidate page URLs were discovered by search. Titles are reviewed separately.
URLS=[
'https://detail.zol.com.cn/1423/1422264/param.shtml',
'https://detail.zol.com.cn/1337/1336958/param.shtml',
'https://detail.zol.com.cn/1402/1401738/param.shtml',
'https://detail.zol.com.cn/1423/1422263/param.shtml',
'https://detail.zol.com.cn/1294/1293683/param.shtml',
'https://detail.zol.com.cn/1395/1394686/param.shtml',
'https://detail.zol.com.cn/1366/1365938/param.shtml',
'https://detail.zol.com.cn/1298/1297117/param.shtml',
'https://detail.zol.com.cn/1291/1290737/param.shtml',
'https://detail.zol.com.cn/1347/1346858/param.shtml',
'https://detail.zol.com.cn/1395/1394657/param.shtml',
'https://detail.zol.com.cn/1321/1320842/param.shtml',
'https://detail.zol.com.cn/1338/1337173/param.shtml',
'https://detail.zol.com.cn/1343/1342330/param.shtml',
'https://detail.zol.com.cn/1395/1394658/param.shtml',
'https://detail.zol.com.cn/1365/1364843/param.shtml',
'https://detail.zol.com.cn/1382/1381407/param.shtml',
'https://detail.zol.com.cn/1309/1308511/param.shtml',
'https://detail.zol.com.cn/1282/1281876/param.shtml',
'https://detail.zol.com.cn/1395/1394685/param.shtml',
'https://detail.zol.com.cn/1395/1394661/param.shtml',
'https://detail.zol.com.cn/1382/1381412/param.shtml',
]


class ParamParser(HTMLParser):
    def __init__(self):
        super().__init__();self.active=None;self.depth=0;self.parts=[];self.values={};self.title=[];self.in_title=False
    def handle_starttag(self,tag,attrs):
        if tag=='title':self.in_title=True
        attrs=dict(attrs)
        if self.active is not None:self.depth+=1
        elif tag=='span' and re.fullmatch(r'newPm(?:Name|Val)_\d+',attrs.get('id','')):
            self.active=attrs['id'];self.depth=1;self.parts=[]
        if tag=='br' and self.active:self.parts.append(' ')
        if tag in ('br','img','input','hr','meta','link') and self.active:self.depth-=1
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        if self.active is not None:
            self.depth-=1
            if self.depth==0:
                self.values[self.active]=''.join(self.parts).strip();self.active=None
    def handle_data(self,data):
        if self.active is not None:self.parts.append(data)
        if self.in_title:self.title.append(data)


def parse(raw):
    charset=re.search(br'charset\s*=\s*["\']?([\w-]+)',raw[:8000],re.I)
    encoding=charset[1].decode() if charset else 'gb18030'
    parser=ParamParser();parser.feed(raw.decode(encoding,errors='replace'))
    fields={}
    for key,name in parser.values.items():
        if key.startswith('newPmName_'):
            loc='newPmVal_'+key.split('_')[-1];value=parser.values.get(loc)
            if value and value!='暂无数据':fields[name]=dict(value=value,locator='#'+loc,source_field=name,raw_value=value,quote=name+'：'+value)
    return ''.join(parser.title),fields


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=Path('docs/homeappliance-params-20261106'));a=ap.parse_args();p=a.output
    (p/'third-party').mkdir(exist_ok=True);path=p/'third-party-captures.json';old=json.loads(path.read_text()) if path.exists() else {}
    def collect(u):
        if u in old and not old[u].get('error'):
            r=old[u];raw=gzip.decompress((p/'third-party'/(r['sha256']+'.html.gz')).read_bytes())
            title,fields=parse(raw);return u,{**r,'title':title,'fields':fields}
        r=dict(url=u,captured_at=datetime.now(timezone.utc).isoformat(),source_type='third_party',source='zol')
        try:
            raw=request(u);sha=hashlib.sha256(raw).hexdigest();(p/'third-party'/(sha+'.html.gz')).write_bytes(gzip.compress(raw,mtime=0));title,fields=parse(raw)
            r.update(sha256=sha,title=title,fields=fields)
        except Exception as e:r['error']=str(e)
        return u,r
    with ThreadPoolExecutor(max_workers=3) as pool:
        for u,r in pool.map(collect,URLS):
            old[u]=r;path.write_text(json.dumps(old,ensure_ascii=False,indent=2));print(u,r.get('title',r.get('error')),len(r.get('fields',{})),flush=True)


if __name__=='__main__':main()
