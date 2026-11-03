"""Freeze a reproducible stratified 20-row review, with distinct Apple/DJI article URLs."""
import json,random,hashlib
from capture import ROOT,save
new=json.load(open(ROOT/'new-candidates.json'));rng=random.Random(20261104)
selected=[]
for prefix,count in [('CN:mi_cn:',1),('CN:dji:',7)]:
 pool=[c for c in new if c['ids'][0].startswith(prefix)];groups={}
 for c in pool:groups.setdefault(c['release']['evidence']['url'],[]).append(c)
 for u in rng.sample(sorted(groups),count):selected.append(rng.choice(groups[u]))
# Ensure CN exact storage/stand and historic model are both inspected; groups selected randomly within strata.
for prefix,count in [('CN:apple_cn:',4),('GLOBAL:apple_support:',8)]:
 pool=[c for c in new if c['ids'][0].startswith(prefix)];groups={}
 for c in pool:groups.setdefault(c['release']['evidence']['url'],[]).append(c)
 for u in rng.sample(sorted(groups),count):selected.append(rng.choice(groups[u]))
assert len(selected)==20
save('review-frozen.json',dict(seed=20261104,universe_sha256=hashlib.sha256(json.dumps(new,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),samples=selected))
for c in selected:
 r=c['release'];e=r['evidence'];print(c['ids'][0],c['name'],r['date'],r['event'],'\n',e['locator'],'\n',e['quote'][:1200],'\n',e['url'],'\n')
