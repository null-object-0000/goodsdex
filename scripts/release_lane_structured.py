#!/usr/bin/env python3
"""Bounded resumable L6. 300 unique gids per source before an explicit full run."""
import argparse
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urljoin,urlparse,quote,unquote,parse_qs,urlencode
import urllib.request
import urllib.error
import base64

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from goodsdex.release_structured import Page,SITES,POLICY,identity,identity_proof,parse_field,fingerprint,apply
from goodsdex.brands import namespace_brand
from goodsdex.release_coverage import matrix


def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temp.replace(path)


class Fetcher:
    def __init__(self,output,live=True):self.output=Path(output).resolve();self.live=live
    def fetch(self,url):
        domain0=urlparse(url).hostname or ''
        circuit=self.output/('blocked-'+domain0+'.json')
        directory=self.output/'captures';directory.mkdir(parents=True,exist_ok=True)
        key=hashlib.sha256(url.encode()).hexdigest();meta=directory/(key+'.json')
        if meta.exists():
            cached=json.loads(meta.read_text())
            if cached.get('status')==403 and cached.get('reason')=='no_page':cached['reason']='access_denied'
            return cached
        if circuit.exists():return dict(url=url,reason='search_challenge_circuit_open')
        if not self.live:return dict(url=url,reason='not_captured')
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs):return None
        opener=urllib.request.build_opener(NoRedirect())
        result=dict(url=url,captured_at=datetime.now(timezone.utc).isoformat())
        target=url
        for _ in range(5):
            host=urlparse(target).hostname or ''
            domain=next((d for d in ('zol.com.cn','pconline.com.cn','baike.baidu.com','bing.com','baidu.com') if host==d or host.endswith('.'+d)),None)
            if not domain:result.update(reason='redirect_not_allowed');break
            throttle=self.output/'throttle';throttle.mkdir(parents=True,exist_ok=True)
            with (throttle/(domain+'.lock')).open('a+') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                stamp=throttle/(domain+'.json');prior=json.loads(stamp.read_text()) if stamp.exists() else {}
                base=1.0 if domain=='bing.com' else 2.1
                interval=max(base,prior.get('interval',base) if prior.get('interval',base)>=10 else base);time.sleep(max(0,prior.get('started',0)+interval-time.time()))
                started=time.time();state=dict(started=started,interval=interval)
                save(stamp,state)
                with (throttle/'requests.jsonl').open('a') as log:log.write(json.dumps(dict(url=target,started=started,phase='start',interval=interval))+'\n')
                try:
                    r=opener.open(urllib.request.Request(target,headers={'User-Agent':'Mozilla/5.0 (compatible; Goodsdex-release-evidence/1.0)'}),timeout=12)
                except urllib.error.HTTPError as e:r=e
                except OSError as e:result.update(reason='transport_error',error=str(e));break
                if r.code in (503,429):
                    state['interval']=max(10,interval*1.5);save(stamp,state)
                try:raw=r.read()
                except OSError as e:result.update(reason='transport_error',error=str(e));break
                with (throttle/'requests.jsonl').open('a') as log:log.write(json.dumps(dict(url=target,started=started,phase='result',status=r.code,interval=interval))+'\n')
            if r.code in (301,302,303,307,308):target=urljoin(target,r.headers['Location']);continue
            path=directory/(key+'.html.gz');path.write_bytes(gzip.compress(raw,mtime=0))
            encoding=r.headers.get_content_charset()
            if not encoding:
                m=re.search(br'charset\s*=\s*["\']?([\w-]+)',raw[:10000],re.I)
                encoding=m.group(1).decode() if m else 'utf-8'
            result.update(status=r.code,final_url=target,capture_file=str(path.relative_to(ROOT)),encoding=encoding,sha256=hashlib.sha256(raw).hexdigest(),reason='retrieved' if r.code==200 else 'rate_limited' if r.code in (503,429) else 'access_denied' if r.code==403 else 'no_page')
            if ('wappass.baidu.com' in target or b'cf-chl-' in raw or '<title>百度安全验证'.encode() in raw):
                result['reason']='search_challenge'
                save(circuit,dict(url=target,reason='search_challenge',captured_at=result['captured_at']))
            break
        else:result['reason']='redirect_limit'
        save(meta,result);return result
    def page(self,capture):
        if capture.get('reason')!='retrieved':return None
        return Page(gzip.decompress((ROOT/capture['capture_file']).read_bytes()).decode(capture['encoding'],errors='replace'))


def allowed(url,site):
    u=urlparse(url)
    return u.scheme in ('http','https') and u.hostname==SITES[site] and (('/item/' in u.path) if site=='baike' else ('/series/' not in u.path and re.search(r'\d',u.path)))


def links(page,site):
    out=[]
    if not page:return out
    for url in page.links:
        if 'bing.com/ck/' in url:
            encoded=parse_qs(urlparse(url).query).get('u',[''])[0]
            if encoded.startswith('a1'):
                try:url=base64.urlsafe_b64decode(encoded[2:]+'===').decode()
                except (ValueError,UnicodeError):continue
        if allowed(url,site) and url not in out:out.append(url)
    return out


def collect_site(site,rows,output,live):
    state_path=output/(site+'-state.json');state=json.loads(state_path.read_text()) if state_path.exists() else {}
    fetcher=Fetcher(output,live)
    def visit(url,row,record):
        if not allowed(url,site):return False
        c=fetcher.fetch(url);record['attempts'].append(c)
        page=fetcher.page(c)
        if not page:
            if c.get('reason') in ('rate_limited','access_denied','search_challenge','search_challenge_circuit_open'):record['reason']='rate_limited_or_challenge'
            elif c.get('reason')=='no_page':record['reason']='no_page'
            return False
        if not allowed(c.get('final_url',url),site):return False
        proof=identity_proof(row,page)
        if not proof:return False
        record.update(url=c.get('final_url',url),match_evidence=proof,match_confidence=proof['confidence'],matched_name=proof['model'],reason='no_field',status='mapped')
        field=parse_field(page,site)
        if not field:
            # Only follow the parameters link belonging to this exact product id.
            product=re.search(r'(?:index)?(\d{5,})',urlparse(url).path)
            for href in page.links:
                parameter=urljoin(url,href)
                if (product and product.group(1) in urlparse(parameter).path and allowed(parameter,site)
                    and re.search(r'param|_detail',parameter) and parameter!=url):
                    cp=fetcher.fetch(parameter);record['attempts'].append(cp);pp=fetcher.page(cp)
                    if pp and identity_proof(row,pp) and parse_field(pp,site):
                        c,page,proof=cp,pp,identity_proof(row,pp);field=parse_field(pp,site)
                        record.update(url=cp.get('final_url',parameter),match_evidence=proof)
                    if pp and parse_field(pp,site) and not identity_proof(row,pp):
                        record['reason']='parameter_identity_mismatch'
                        record['parameter_rejection']=dict(url=parameter,headings=pp.headings,field=parse_field(pp,site))
                    break
        if field:record.update(status='hit',reason='structured_field',field=field,evidence=dict(c,url=record['url'],quote=field['quote'],identity_quote=proof['body_quote'],source_type='third_party',locator=field['label']))
        return True
    for i,row in enumerate(rows):
        gid=row['id'];fp=fingerprint(row)
        if gid in state and state[gid].get('identity_sha256')==fp and state[gid].get('collector_version')==5:continue
        record=dict(id=gid,name=row['name'],brand=row.get('brand') or namespace_brand(gid),identity_sha256=fp,site=site,collector_version=5,attempts=[],status='missing',reason='unable_to_map')
        term=identity(row)
        if not term:record['reason']='ambiguous_model_or_configuration'
        else:
            matched=site=='baike' and visit('https://baike.baidu.com/item/'+quote(term),row,record)
            if not matched:
                query=(record['brand'] or '')+' "'+term+'" site:'+SITES[site]
                for engine in ('bing','baidu'):
                    search_url=('https://cn.bing.com/search?'+urlencode({'q':query})) if engine=='bing' else ('https://www.baidu.com/s?'+urlencode({'wd':query}))
                    search=fetcher.fetch(search_url);record['attempts'].append(dict(search,kind='exact_brand_model_site_search'))
                    if search.get('reason') in ('rate_limited','access_denied','search_challenge','search_challenge_circuit_open'):
                        record.setdefault('discovery_failures',[]).append(dict(engine=engine,reason=search['reason']))
                        if not any(a.get('kind')=='exact_brand_model_site_search' and a.get('reason')=='retrieved' for a in record['attempts']):record['reason']='rate_limited_or_challenge'
                    if any(visit(url,row,record) for url in links(fetcher.page(search),site)[:3]):break
        state[gid]=record;save(state_path,state)
        print(f'L6 {site} {i+1}/{len(rows)} {gid} {record["reason"]}',flush=True)
    return [state[r['id']] for r in rows]


def sample_rows(rows,limit=300):
    # Stable stratified sample: every brand represented, phones/tablets enriched within brand.
    groups=defaultdict(list)
    for row in rows:groups[row.get('brand') or namespace_brand(row['id']) or '未知'].append(row)
    for group in groups.values():group.sort(key=lambda r:(not bool(re.search('手机|平板|红米|REDMI|Redmi|小米\\d|小米 \\d',r['name'])),hashlib.sha256(r['id'].encode()).hexdigest()))
    result=[];seen=set()
    while any(groups.values()) and len(result)<limit:
        for brand in sorted(groups):
            if groups[brand] and len(result)<limit:
                row=groups[brand].pop(0)
                if row['id'] not in seen:result.append(row);seen.add(row['id'])
    return result


def stats(records):
    captures={a['url']:a for r in records for a in r['attempts'] if a.get('captured_at') and not a.get('kind')}
    return dict(attempted=len(records),queried=sum(bool(r['attempts']) for r in records),
                source_page_captures=len(captures),source_status=dict(Counter(str(c.get('status') or c['reason']) for c in captures.values())),
                circuit_skips=sum(sum(a.get('reason')=='search_challenge_circuit_open' for a in r['attempts']) for r in records),
                mapped=sum('url' in r for r in records),hits=sum(r['status']=='hit' for r in records),
                confidence=dict(Counter(r['match_confidence'] for r in records if 'url' in r)),
                precision=dict(Counter(r['field']['granularity'] for r in records if r['status']=='hit')),
                reasons=dict(Counter(r['reason'] for r in records)))


def run(rows,output,*,live=True,full=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    selected=rows if full else sample_rows(rows)
    capability=output/'site-search-capabilities.json'
    if not capability.exists():
        probe=Fetcher(output,live).fetch('https://search.pconline.com.cn/product.jsp?kw=%E7%BA%A2%E7%B1%B36')
        save(capability,dict(zol=dict(status='known_unavailable_not_retried',reason='DSH service.zol.com.cn unavailable'),pconline=probe))
    # Full is an explicit operator decision, never an automatic consequence of a failed pilot.
    if full and not (output/'sample-summary.json').exists():raise ValueError('Run 300-gid pilot first')
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs={s:pool.submit(collect_site,s,selected,output,live) for s in SITES}
        records=[r for job in jobs.values() for r in job.result()]
    entries=[r for r in records if r['status']=='hit']
    index={r['id']:dict(zol_url=None,pconline_url=None,baike_url=None,matched_name=None,match_confidence=None,status='unprocessed',processed_sites=[]) for r in rows}
    for row in selected:
        rs=[r for r in records if r['id']==row['id']];mapped=[r for r in rs if r.get('url')]
        index[row['id']]={**{s+'_url':next((r['url'] for r in mapped if r['site']==s),None) for s in SITES},'status':'mapped' if mapped else 'unmapped','processed_sites':list(SITES),'matched_name':mapped[0]['matched_name'] if mapped else None,'match_confidence':mapped[0]['match_confidence'] if mapped else None,'evidence':{r['site']:dict(r['match_evidence'],capture=next((c for c in r['attempts'] if c.get('final_url')==r['url']),None)) for r in mapped}}
    ip=ROOT/'data/official/third_party_index.json';prior=json.loads(ip.read_text()) if ip.exists() else {};prior={**index,**prior};prior.update({k:v for k,v in index.items() if v['processed_sites']});save(ip,prior)
    summary={s:dict(stats([r for r in records if r['site']==s]),brands={b:stats([r for r in records if r['site']==s and r['brand']==b]) for b in sorted({r['brand'] or '未知' for r in records})}) for s in SITES}
    bundle=dict(lane='L6',policy=POLICY,mode='full' if full else 'sample300',entries=entries,records=records,summary=summary,baike_downgraded=sum(e['field']['baike_downgraded'] for e in entries))
    save(output/('full-summary.json' if full else 'sample-summary.json'),summary);save(output/'result.json',bundle)
    # Only selected gids are replaced; pilot replay cannot erase a previous full collection.
    target=ROOT/'data/third-party/l6-release-evidence.json'
    old=json.loads(target.read_text()) if target.exists() else {}
    gids={r['id'] for r in selected}
    bundle['entries']=[e for e in old.get('entries',[]) if e['id'] not in gids]+entries
    save(target,bundle)
    after=apply(rows,bundle)
    save(output/'coverage.json',dict(before=matrix(rows),after=matrix(after),mode=bundle['mode']))
    save(output/'conflicts.json',[dict(id=r['id'],name=r['name'],review=r['release_structured_review']) for r in after if r.get('release_structured_review')])
    return bundle


def append_report(lines,before,after,bundle,output):
    lines.extend(['','## L6：ZOL / 太平洋 / 百度百科', '', '模式：'+bundle['mode']+'；抽样按品牌轮转、品牌内优先手机/平板；不是随机总体命中率估计。', '', '| 来源 | 尝试 | 映射 | 日期命中 | 精度 | 失败原因 |','|---|---:|---:|---:|---|---|'])
    for s,v in bundle['summary'].items():lines.append(f"| {s} | {v['attempted']} | {v['mapped']} | {v['hits']} | {v['precision']} | {v['reasons']} |")
    lines.extend(['','| 来源 / 品牌 | 尝试 | 映射 | 置信度分布 |','|---|---:|---:|---|'])
    for s,v in bundle['summary'].items():
        for b,c in v['brands'].items():lines.append(f"| {s} / {b} | {c['attempted']} | {c['mapped']} | {c['confidence']} |")
    official=0;official_conflicts=0;conflicts=0
    for r in after:
        official_conflicts+=bool(r.get('release_structured_official_conflicts'))
        if r.get('release_structured_review'):conflicts+=1
        elif r.get('release_structured_crosschecks') and (r.get('release') or {}).get('source') in ('official','official_hidden'):official+=1
    lines.extend(['',f"百度百科日→月降级 {bundle['baike_downgraded']} 条。官方日期保留/交叉核对 {official} 条（日期不一致 {official_conflicts} 条，均保留官方）；L5/跨站冲突待核对 {conflicts} 条（冲突留空，清单 L6/conflicts.json）。",'',f"L6应用前 {matrix(before)['total']}；应用后 {matrix(after)['total']}。",'', '### 可复核案例（不足10条如实列出）'])
    for e in bundle['entries'][:10]:
        f=e['field'];lines.extend([f"- {e['name']} / {e['id']}：{f['date']} ({f['granularity']})。{e['evidence']['url']}",f"  原文：{f['quote']}；"+('百科日精度默认降到月' if f['baike_downgraded'] else '结构化字段明确到'+('日' if f['granularity']=='day' else '月'))])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--goods',type=Path,required=True);p.add_argument('--output',type=Path,default=ROOT/'docs/release-coverage/L6');p.add_argument('--full',action='store_true');p.add_argument('--no-live',action='store_true');a=p.parse_args()
    r=json.loads(a.goods.read_text());b=run(r,a.output,live=not a.no_live,full=a.full);print(json.dumps(b['summary'],ensure_ascii=False))
