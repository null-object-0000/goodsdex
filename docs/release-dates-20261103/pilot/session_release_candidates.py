import sys,json,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
# Evidence-constrained candidates authored by the interactive Codex LLM after
# reading the source snippets. This is NOT another model API call.
specs=[
('111841','be40bb0ad755d943','2022-10'),('111842','be40bb0ad755d943','2022-10'),
('111843','95d9dfa400db1eff','2023-02'),('111847','279e260a89d5f3af','2021-04'),
('111852','490e771b9116d442','2022-09'),('111854','c366d07e8e5dbc4a','2022-10'),
('111858','0228692a33558056','2020-12'),('111863','2b63ec943203932e','2021-10'),
('111867','b44c6eb48658b3d8','2022-07'),
('111870','d4c931e355b5d722','2021-09'),('111871','d4c931e355b5d722','2021-09'),
('111872','9f42bb69e0d6bb4d','2021-09'),('111873','9f42bb69e0d6bb4d','2021-09'),
('111874','eaa7e5b05a8f9262','2020-11'),('111875','eaa7e5b05a8f9262','2020-10'),
('111876','225722eefb98e77a','2020-10'),('111877','225722eefb98e77a','2020-11'),
('111886','9c84e994b11c371e','2021-09'),('111887','e3732d86a7cea95d','2022-03'),
('111890','62b97a53d6120955','2022-03'),('111895','059ab82323152837','2021-05'),
('111896','519d203bb75b8d25','2021-05'),('111897','519d203bb75b8d25','2021-05'),
('111898','d4c931e355b5d722','2021-09'),('111900','62b97a53d6120955','2022-03'),
('111901','f1ab0c9a3bf12d81','2021-10'),('111902','f1ab0c9a3bf12d81','2021-10'),
('111905','24d5298aa553e3ca','2020-10'),('111933','740ef6345e947b47','2018-11'),
('111974','d6eb725449521144','2018-11'),('111979','d6eb725449521144','2018-11'),
('111340','619c82298265a459','2023-02'),('111838','619c82298265a459','2023-02'),
('111832','0bf872dda7e5dd8f','2023-09'),('118451','267ef4c673d2ebae','2020-09'),
('118453','7087e4d8507a054f','2019-09'),
('117735','1a4b280aff17cf44','2023-11'),('117736','1a4b280aff17cf44','2023-11'),('117737','1a4b280aff17cf44','2023-11')]
root=Path('docs/release-dates-20261103');out=root/'llm';rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'));byid={r['id']:r for r in rows};values=[];families=[];documents=[]
for id,key,date in specs:
 family='GLOBAL:apple_support:model:'+id;r=byid[family];doc=json.loads((root/'evidence'/f'{key}.json').read_text());t=doc['text'];m=int(date[5:])
 # Locate the exact source sentence selected by the LLM, retaining enough text
 # for split availability and the document's explicit publication-year anchor.
 if id in ['111870','111871','111898']:start=t.index('2021 年 9 月 24 日');q=t[start:start+310]
 elif id=='111895':start=t.index('设计格外紧凑');q=t[start:start+260]
 elif id in ['111896','111897']:
  start=t.index('五月中下旬开始发售');q=t[max(0,start-190):start+100]
 elif id=='111905':start=t.index('全新 iPad Air 将于十月');q=t[max(0,start-100):start+110]
 elif id=='111933':start=t.index('11 月 7 日');q=t[max(0,start-160):start+140]
 elif id=='111974' or id=='111979':start=t.index('11 月 7 日');q=t[max(0,start-155):start+140]
 else:
  # Month here comes from the LLM-authored candidate above, not from model year.
  pattern=rf'{m} 月 \d+ 日[^。]{{0,100}}(?:发售|发货|有售)'
  matches=list(re.finditer(pattern,t))
  if not matches:raise ValueError((id,key,date))
  a=matches[0];q=t[max(0,a.start()-170):a.end()+125]
 assert q in t
 values.append(dict(family=family,date=date,document=key,quote=q,confidence='high',reason='对照规格页型号/尺寸/代次与官网公告；取正文开售月，非预购或新闻稿月份。'))
 families.append(dict(family=family,name=r['name'],ids=[family]));documents.append(dict(key=key,url=doc['url'],title=t[:110],quote=q))
prompt='交互会话内由 Codex LLM 阅读官网原文，按精确机型/代次/尺寸生成开售月候选；保持 source=llm，不使用记忆，无依据留空。抽样复核前不可发布。'
(out/'input-session.json').write_text(json.dumps(dict(prompt=prompt,families=families,documents=documents),ensure_ascii=False,indent=1))
(out/'batch-session.json').write_text(json.dumps(dict(model='codex-interactive-session',captured_at=datetime.now(timezone.utc).isoformat(),input_sha256=hashlib.sha256(prompt.encode()).hexdigest(),additional_gateway_calls=0,response=dict(choices=[dict(finish_reason='stop',message=dict(content=json.dumps(dict(candidates=values),ensure_ascii=False)))])),ensure_ascii=False,indent=1))
print('session LLM families',len(values),'extra gateway calls',0)
