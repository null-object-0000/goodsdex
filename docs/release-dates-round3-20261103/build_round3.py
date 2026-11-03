"""Replay reviewed exact products from captured official announcements.

This is an explicit allowlist. Discovery substring hits are never auto-published.
"""
import json,re,sys,hashlib
from pathlib import Path
sys.path.insert(0,'src')
from goodsdex.release_dates import validate,apply_release_dates,coverage
from capture import ROOT,get
rows=json.load(open(sys.argv[1] if len(sys.argv)>1 else '/tmp/goodsdex-round3-before.json'))
for r in rows:
    if (r.get('release') or {}).get('family','').startswith('round3:'):r.pop('release')
by={r['id']:r for r in rows}
bundle=json.load(open('data/official/release-dates.json'))
bundle['candidates']=[c for c in bundle['candidates'] if not c['family'].startswith('round3:')]
new=[];decisions=[]

def add(key,date,o,quote,event,identity=None,locator=None):
    assert key in by and not by[key].get('release'),key
    assert quote in o['text'],(key,'non-verbatim quote')
    assert o['http_status']==200
    ev=dict(url=o['url'],quote=quote,locator=locator or 'dated Chinese press release / exact named product in sale section',sha256=o['sha256'],captured_at=o['captured_at'],source_type='official')
    if identity:ev['identity_evidence']=identity
    r=dict(date=date,granularity='month',source='official',confidence='high',event=event,market='CN',evidence=ev)
    c=dict(family='round3:'+key,ids=[key],name=by[key]['name'],category=by[key].get('category'),method='explicit_dated_statement',release=r)
    validate(c);new.append(c)

def dji(slug,skus,event='availability',aliases=None):
    o=get('https://www.dji.com/cn/media-center/announcements/'+slug);s=o['text']
    stamp=re.search(r'20\d\d-\d\d-\d\d',s);assert stamp
    headings=['售价与服务','发售与服务','售价与详情','发售与售价','售价与支持','发售价格','售后与服务']
    starts=[s.index(h) for h in headings if h in s];assert starts,(slug,'no sale section')
    start=min(starts);end=s.find('适用于',start)
    if end<0:end=s.find('更多关于',start)
    if end<0:end=s.find('了解',start)
    if end<0:end=s.find('探索更多',start)
    quote=s[start:end].strip()
    if event=='availability':assert any(t in quote for t in ['即日起','现货发售','正式开售']),slug
    for sku in skus.split():
        key='CN:dji:sku:'+sku
        identity=None
        if aliases and sku in aliases:
            identity=dict(reason=aliases[sku],url=by[key]['source_url'],packaging=by[key].get('params',{}).get('包装清单',[]))
        add(key,stamp[0][:7],o,quote,event,identity,
            'article header '+stamp[0]+' / '+s[start:start+10])

# Individually enumerated sale configurations and separately sold transmitters.
dji('dji-release-mic-mini-cn','177861 177891 177921 177951')
dji('dji-release-osmo-mobile-8p','219081 219141 219171')
dji('dji-release-mic-3','197721 197751 197781')
dji('dji-release-mic-mini-2s','241731 241761 241791 241821')
dji('dji-release-osmo-action-6','207351 207381',aliases={'207381':'畅拍套裝 is the traditional-character spelling of 畅拍套装; exact camera and package.'})
dji('dji-release-rs-4-mini','183261 183291')
dji('dji-release-air-3s-cn','173511 173541 173571',aliases={
 '173511':'普通遥控器 = DJI RC-N3; original exact-vid packaging has RC-N3 quantity 1, RC 2 quantity 0.',
 '173541':'畅飞/普通遥控器 = RC-N3, three batteries; original exact-vid packaging.',
 '173571':'畅飞/带屏遥控器 = RC 2, three batteries; original exact-vid packaging.'})
dji('dji-launches-ronin-4d-flex','134661')
dji('dji-release-mini-5-pro','199551 199612 199671')
dji('dji-osmo-action-5-pro-cn','170301 170331')
dji('dji-pro-launches-next-generation-tools-cn','163911 163971 164001 164031 164061')
dji('dji-release-mavic-4-pro-cn','189291 189351 189411')
dji('dji-release-osmo-pocket-4','218422 218481')
dji('dji-release-osmo-nano','198471 198892')
dji('osmo-action-4-cn','144651 144681',aliases={
 '144651':'本文先明确“标准套装及全能套装版两种”，售价段将标准套装简称标准版；没有添加其他配件。',
 '144681':'全能套装与全能套装版文字等价，原始包装为三电池及1.5米延长杆。'})
dji('osmo-mobile-7-series','182961 182991')
dji('dji-launch-sdr-transmission-cn','168621 168651 168681')
dji('dji-release-osmo-360-2','261561 261772')
dji('dji-release-neo-2','204831 204861 205221 205521')
dji('dji-release-rs3mini-cn','130881')
dji('dji-release-flip','181131 181161 181191',aliases={
 '181131':'普通遥控器版与普通遥控器为官方同一套装名称。',
 '181161':'带屏遥控器版与带屏遥控器为官方同一套装名称。'})
dji('dji-release-osmo-360','194091 194271')
dji('dji-neo-cn','169761 169791',aliases={'169761':'本文单机版=无人机加一电池、不含遥控器；原始 exact-vid 包装 RC-N3 数量0。'})
dji('dji-release-avata-360','214791 215061 215091 215181')
dji('dji-release-lito-x1-lito-1','220251 220431 220433 220792 221302 222113')
dji('dji-release-mic-mini-2','218871 218901 218931 218991 219021')
dji('dji-o4-air-unit','180741')
dji('power-1000-mini','212451')
dji('dji-release-power-1000-v2','188181')
dji('dji-release-power-2000','184911')
# This article promises June delivery; April is only its announcement.
dji('dji-launches-dji-inspire-3','136551',event='announcement',aliases={'136551':'79888元套装与原始 exact-vid 包装（RC Plus、6块TB51、PROSSD 1TB）一致；不向后续基础版传递。'})

# Chinese press releases announce exact bodies/lenses; never inherit to camera kits.
fuji=[('model:x-m5','3915'),('model:x-t50','3883'),('model:x-hf1','3969'),('model:x-e5','3976'),('model:x-t30-iii','4004'),
 ('lens:xc13-33mmf35-63-ois','4003'),('lens:xf16-50mmf28-48-r-lm-wr','3884'),('lens:xf16-55mmf28-r-lm-wr-ii','3916'),
 ('lens:xf500mmf56-r-lm-ois-wr','3917'),('lens:xf23mmf28-r-wr','3975'),('lens:xf400mmf45-r-lm-ois-wr','4073')]
for model,pid in fuji:
    o=get('https://www.fujifilm.com.cn/cn/zh-hans/news/detail/'+pid);s=o['text']
    stamp=re.search(r'(20\d\d)年(\d{1,2})月(\d{1,2})日',s);assert stamp
    start=s.rfind('新闻稿',0,stamp.start());start=start if start>=0 else stamp.start()
    quote=s[start:stamp.end()+600]
    add('CN:fuji:'+model,f'{stamp[1]}-{int(stamp[2]):02}',o,quote,'announcement',locator='China press release header date and exact new product announcement; no CN sale claim')

# Publicly rendered company timeline, not a hidden goods parameter.
o=get('https://www.mi.com/about/history');timeline=json.load(open(ROOT/'mi-history-structured.json'))
for pid,year,month,needle in [('3488','2016','03','3月29日小米公司正式启用MIJIA米家品牌，专注于智能家庭和提升用户生活品质，并发布首款米家品牌产品——米家压力IH电饭煲。'),('6334','2017','07','7月26日小米首款人工智能音箱小米AI音箱、人工智能助理小爱同学正式发布。')]:
    section=next(x[year] for x in timeline['data'] if year in x)
    assert needle in section[month]
    # Attach separately hashed public timeline data; raw HTTP evidence retained too.
    ev=dict(o);ev['text']=needle
    add('CN:mi_cn:product:'+pid,year+'-'+month,ev,needle,'announcement',locator=f'visible about_history timeline / {year}/{month}; $GLOBAL_PAGE.PageData.main_body json_component; rendered in browser')

assert len({c['ids'][0] for c in new})==len(new)
oldids={k for c in bundle['candidates'] for k in c['ids']};assert not oldids.intersection({c['ids'][0] for c in new})
bundle['candidates']+=new
Path('data/official/release-dates.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
(ROOT/'new-candidates.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')
output=apply_release_dates(rows)
(ROOT/'coverage.json').write_text(json.dumps(dict(before=coverage(rows),after=coverage(output),row_count_delta=len(output)-len(rows),new_dates=len(new),added_rows=sum(bool(r.get('release')) for r in output)-sum(bool(r.get('release')) for r in rows)),ensure_ascii=False,indent=2)+'\n')
print('added',len(new));print(json.dumps(coverage(output),ensure_ascii=False))
