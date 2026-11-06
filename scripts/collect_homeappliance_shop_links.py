"""Probe baike's explicit official shop product IDs; never guess by product name."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from collect_homeappliance_params import request, MTOP_URL, MTOP_HEADERS


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=Path('docs/homeappliance-params-20261106'))
    a = ap.parse_args(); p = a.output
    caps = json.loads((p/'captures.json').read_text()); targets = json.loads((p/'targets.json').read_text())
    bridges = {}
    for t in targets:
        c = caps.get(str(t['model'])+':product', {})
        if t['had_params'] or not c.get('sha256'): continue
        d = json.loads(gzip.decompress((p/'raw'/(c['sha256']+'.json.gz')).read_bytes())).get('data') or {}
        u = (d.get('buyUrl') or {}).get('channelUrl', '')
        parsed = urlsplit(u); q = parse_qs(parsed.query)
        pid = (q.get('product_id') or q.get('commodityId') or [''])[0]
        if parsed.hostname not in ('www.mi.com', 'm.mi.com') or not pid.isdigit(): continue
        bridges[t['id']] = dict(model=t['model'], url=u, pid=pid, product_sha256=c['sha256'])
    (p/'shop-bridges.json').write_text(json.dumps(bridges, ensure_ascii=False, indent=2))
    pids = sorted({v['pid'] for v in bridges.values()}); path=p/'shop-captures.json'
    results = json.loads(path.read_text()) if path.exists() else {}
    def collect(pid):
        if pid in results and 'error' not in results[pid]: return pid,results[pid]
        body = json.dumps([{}, {'productId': pid}]).encode()
        r = dict(url=MTOP_URL, method='POST', body=body.decode(), captured_at=datetime.now(timezone.utc).isoformat())
        try:
            raw=request(MTOP_URL,body,MTOP_HEADERS);d=json.loads(raw)
            # Capture both product-only and default-gid requests, as the normal collector does.
            gid=((d.get('data') or {}).get('product') or {}).get('defaultGid')
            if d.get('code')==0 and gid:
                body=json.dumps([{}, {'productId':pid,'gid':gid}]).encode()
                raw2=request(MTOP_URL,body,MTOP_HEADERS); d2=json.loads(raw2)
                if d2.get('code')==0: raw=raw2;r['body']=body.decode()
            sha=hashlib.sha256(raw).hexdigest();(p/'raw'/(sha+'.json.gz')).write_bytes(gzip.compress(raw,mtime=0))
            r['sha256']=sha
        except Exception as e:r['error']=str(e)
        return pid,r
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,(pid,r) in enumerate(pool.map(collect,pids),1):
            results[pid]=r;path.write_text(json.dumps(results,ensure_ascii=False,indent=2))
            if i%20==0: print(i,'/',len(pids),flush=True)
    print('done',len(pids),flush=True)


if __name__=='__main__':main()
