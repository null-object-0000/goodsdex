import json,sys,hashlib,concurrent.futures,re
from pathlib import Path
from datetime import datetime,timezone
sys.path[:0]=['/tmp','src'];from release_probe import get
from goodsdex.release_dates import digest,llm_gate
path=Path('/tmp/release-candidate-review.json');b=json.loads(path.read_text());cs={c['family']:c for c in b['candidates']}
# Adjudicated by reading the original official availability sentences and model
# identity above. Separate expected values, not copied from model predictions.
expected={'111843':'2023-02','111858':'2020-12','111863':'2021-10','118451':'2020-09','111870':'2021-09','111854':'2022-10','111841':'2022-10','111874':'2020-11','111852':'2022-09','118461':'2019-12','111872':'2021-09','111896':'2021-05','111847':'2021-04','117737':'2023-11','111886':'2021-09','111974':'2018-11','111905':'2020-10','111898':'2021-09','111890':'2022-03','111902':'2021-10','111887':'2022-03','111897':'2021-05','111900':'2022-03','111933':'2018-11','111979':'2018-11','111340':'2023-02','111832':'2023-09','111842':'2022-10','111873':'2021-09','117735':'2023-11'}
urls=list(dict.fromkeys(s['verification_url'] for s in b['review']['samples']));fresh={o['url']:o for o in concurrent.futures.ThreadPoolExecutor(6).map(get,urls)}
out=Path('docs/release-dates-20261103/sample-check');out.mkdir(exist_ok=True)
for s in b['review']['samples']:
 c=cs[s['family']];o=fresh[s['verification_url']];assert not o.get('error'),o
 quote=c['release']['evidence']['quote'].split(' | ',1)[1];assert quote in o['text'],('changed source',s['family'])
 key=s['family'].split(':')[-1];s['correct_date']=expected[key];s['correct']=c['release']['date']==expected[key]
 s['verification_quote']=quote;s['checked_at']=datetime.now(timezone.utc).isoformat();s['verification_sha256']=o['sha256'];s['reviewer']='Codex agent: source comparison; no claim of independent human sign-off'
 (out/(hashlib.sha256(o['url'].encode()).hexdigest()[:16]+'.json')).write_text(json.dumps(dict(url=o['url'],sha256=o['sha256'],quote=quote,checked_at=s['checked_at']),ensure_ascii=False,indent=1))
print(llm_gate(b['candidates'],b['review']))
Path('data/official/release-dates.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
Path('docs/release-dates-20261103/sample-review.json').write_text(json.dumps(b['review'],ensure_ascii=False,indent=2)+'\n')
