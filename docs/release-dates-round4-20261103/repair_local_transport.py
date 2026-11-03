"""Reattempt only local transport errors, not denied/blocked HTTP responses."""
import json
from capture import *
failed=json.load(open(ROOT/'failed-sources.json'));out=[]
for x in failed:
 if 'unknown url type: socks5h' not in x.get('error',''):continue
 o=get(x['url']);out.append(o);save('local-transport-recheck.json',out)
print('rechecked',len(out),[(o['http_status'],o['bytes']) for o in out])
