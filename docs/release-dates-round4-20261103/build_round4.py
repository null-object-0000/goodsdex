"""Reviewed exact-ID allowlist. Discovery never automatically publishes a substring hit."""
import json,re,sys,hashlib,unicodedata
from pathlib import Path
sys.path.insert(0,'src')
from goodsdex.release_dates import validate,apply_release_dates,coverage
from capture import *
rows=json.load(open('/tmp/goodsdex-round4-before.json'));by={r['id']:r for r in rows};new=[]
def add(key,date,o,quote,event,identity):
 assert key in by and not by[key].get('release'),key
 assert quote in o['text'],key
 assert o['http_status']==200 and o.get('sha256') and o.get('captured_at'),key
 ev=dict(url=o['url'],quote=quote,locator=identity,sha256=o['sha256'],captured_at=o['captured_at'],source_type='official')
 c=dict(family='round4:'+key,ids=[key],name=by[key]['name'],capture_file=str(Path(o['evidence_file']).relative_to(Path.cwd())) if Path(o['evidence_file']).is_absolute() else o['evidence_file'],method='explicit_dated_statement',release=dict(date=date,granularity='month',source='official',confidence='high',event=event,market='CN',evidence=ev))
 validate(c);new.append(c)
def dji(slug,skus,start,end,event='availability',identity='Exact separately priced product/configuration in Chinese announcement; header anchors 即日起'):
 o=get('https://www.dji.com/cn/media-center/announcements/'+slug);s=o['text'];p=s.index(start);q=s.index(end,p)+len(end);quote=s[p:q]
 date=re.search(r'20\d\d-\d\d-\d\d',s)[0][:7]
 assert event!='availability' or re.search('即日起|正式开售|正式发货',quote)
 for sku in skus.split():add('CN:dji:sku:'+sku,date,o,quote,event,identity)
# All seven are individually named/priced; never propagate to their contents.
dji('dji-release-sdr-transmission-2','265671 265701 265731 265761 265791 265821 265851','发售政策','渠道正式发售。')
dji('dji-release-rs-5','209931 209961','DJI RS 5 售价','渠道正式发售。',identity='RS 5 base and 套装版 separately priced; 套装 equals 套装版, excludes later SDR bundles')
# 开售预约 is not availability. Black and explicitly introduced pearl-white are named in article.
dji('dji-release-osmo-pocket-4p','241282 241311','产品与售价','USB 3.1）等配件。','announcement',identity='2026-06-15 new Pocket 4P announcement; exact standard/Vlog packages; 开售预约 is announcement only')
dji('power-fast-charger-cn','177471','发售价格','渠道正式发售。')
dji('dji-power-release-expansion-battery-2000','173061','发售价格','正式发售；')
dji('dl-75mm-lens-cn','169731','售价与信息','开始同步发售。')
dji('dji-release-transmission-cn','146361 146391 138831','DJI Transmission 图传接收器标准套装、','即日起均已正式开售。',identity='New 2023 standard receiver package, standalone receiver, and RS cable are explicitly named; excludes pre-existing high-monitor set/transmitter')
dji('dji-release-mavic3-pro-cn','137751 137781','Mavic 3 Pro系列分四个版本发售。','渠道正式发售。',identity='RC Pro named in both exact Fly More / Cine Master configurations; 遥控器 is explicit RC Pro, no RC swap')
# 2022 is a planned sale, so retain only exact configuration announcement, not sale month.
dji('dji-release-rs3-rs3pro','116751 116781','售价与服务','详细信息请留意后续官方信息。','announcement',identity='2022-06-15 explicit Transmission set with high-bright monitor and separately priced transmitter; September was only a plan')
# X9-8K rejected in frozen audit: standalone price in 2023 does not establish its first announcement.
# Public timeline announcement: exact body and day, no award date / series-prefix match.
o=get('https://www.mi.com/about/history');timeline=json.load(open('docs/release-dates-round3-20261103/mi-history-structured.json'))
quote='5月31日小米正式发布小米8透明探索版，它是全球首款压感屏幕指纹识别手机 、安卓首款“Face ID” 手机、全球首款双频GPS手机。'
assert any(quote in str(b.get('2018',{}).get('05','')) for b in timeline['data'])
# quote is decoded public JSON component, not visible HTML text. Preserve the extraction locator.
o=dict(o,text=quote)
add('CN:mi_cn:product:8382','2018-05',o,quote,'announcement','public about_history JSON component / 2018 / 05; exact 5月31日 announcement, not a sale claim; structured capture round3/mi-history-structured.json')
# Apple recipes supplied below: exact model identities; date is explicit announcement, not implied sale.
recipes_paths=[ROOT/'apple-reviewed-recipes.json',ROOT/'apple-cn-reviewed-recipes.json']
for recipes_path in recipes_paths:
 if not recipes_path.exists():continue
 for a in json.load(open(recipes_path)):
  o=get(a['url']);s=o['text'];p=s.index(a['start']);q=s.index(a['end'],p)+len(a['end']);quote=s[p:q]
  assert a['identity_token'] in s
  for key in a['ids']:add(key,a['date'],o,quote,a.get('event','announcement'),a['identity'])
assert len({c['ids'][0] for c in new})==len(new)
bundle=json.load(open('data/official/release-dates.json'));bundle['candidates']=[c for c in bundle['candidates'] if not c['family'].startswith('round4:')];bundle['candidates']+=new
Path('data/official/release-dates.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n');save('new-candidates.json',new)
after=apply_release_dates(rows);save('coverage.json',dict(before=coverage(rows),after=coverage(after),added_rows=sum(bool(r.get('release')) for r in after)-sum(bool(r.get('release')) for r in rows),new_ids=len(new)))
print('new',len(new));print(json.dumps(coverage(after),ensure_ascii=False))
