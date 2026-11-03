import json,sys,urllib.request,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
sys.path[:0]=['src','scripts'];from collect_release_candidates import prepare,PROMPT
from goodsdex.vision_extract import _api_key,GATEWAY
out=Path('docs/release-dates-20261103/llm');rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'));bundle=json.load(open('data/official/release-dates.json'));families,batches=prepare(rows,bundle,Path('docs/release-dates-20261103/evidence'))
# Deliberately small evidence-matched pilot, still counting interrupted attempt #4.
(out/'attempt-4.json').write_text(json.dumps(dict(status='interrupted',request_sent=True,reserved_output_tokens=7000,reason='Earlier 7000-token reasoning budget yielded no candidates; no retry of this batch')))
docs={d['key']:d for b in batches for d in b['documents']}
# Families with a clear explicit identity in an availability source. Model still
# decides vintage, region, and exact sale month; literal text is not enough alone.
selected=[]
for f in families.values():
 if not f['family'].startswith('GLOBAL:apple_support:'):continue
 n=f['name'];nm=re.sub(r'[（(].*','',n).strip().lower()
 if n.startswith('iPhone') and re.search(r'iPhone (?:XR|11$|12|13|14$|14 Plus|SE（第 3)',n):selected.append(f)
 elif any(k in n for k in ['2022','2021','2020','2019','2018','2017']) and any(k in n for k in ['iPad','MacBook','iMac','Mac mini','Mac Pro']):selected.append(f)
 elif n.startswith(('AirPods','Apple Watch')) and any(k in n for k in ['Series 8','Ultra','Series 9','Series 5','SE（第 2','AirPods 3','AirPods Max 1']):selected.append(f)
# ~60 families, two requests. Failed/ambiguous families are permitted to abstain.
selected=sorted(selected,key=lambda f:f['family'])[:60]
plan=dict(total_attempts_limit=6,previous_attempts=4,remaining_calls=2,remaining_output_tokens=14000,reasoning_effort='low',families=len(selected))
(out/'revised-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2));print(plan,flush=True)
for i,chunk in enumerate([selected[:30],selected[30:]],5):
 docset=[d for d in docs.values() if int(d['url'].split('/')[4])<=2023]
 data=dict(families=chunk,documents=docset)
 prompt=PROMPT+'\n最多输出30条；quote用最短完整开售句，reason最多40字；尽快给JSON，不展开长推理。\n'+json.dumps(data,ensure_ascii=False)
 request=dict(model='flowlet-flash',messages=[dict(role='user',content=prompt)],temperature=0,max_tokens=7000,reasoning_effort='low')
 (out/f'input-{i}.json').write_text(json.dumps(data,ensure_ascii=False,indent=1))
 req=urllib.request.Request(GATEWAY+'/v1/chat/completions',data=json.dumps(request).encode(),headers={'Authorization':'Bearer '+_api_key(),'Content-Type':'application/json'})
 op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 with op.open(req,timeout=240) as r:result=json.load(r)
 (out/f'batch-{i}.json').write_text(json.dumps(dict(model='flowlet-flash',captured_at=datetime.now(timezone.utc).isoformat(),input_sha256=hashlib.sha256(prompt.encode()).hexdigest(),response=result),ensure_ascii=False,indent=1))
 print('batch',i,result.get('usage'),result['choices'][0].get('finish_reason'),flush=True)
