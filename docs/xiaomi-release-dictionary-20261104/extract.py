"""Reviewed explicit statements only. No publication timestamps as launch dates."""
from pathlib import Path
import json,re,gzip,hashlib,unicodedata,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from goodsdex.release_dates import digest
from goodsdex.series_release import identity

def read(p):return json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s)).casefold()
def compact(s):return re.sub(r'\s+','',s)
entries=[]
def add(name,date,evidence,aliases=(),scope='CN',origin='archive',event='announcement',match='exact'):
    key=norm(name)+'|'+date+'|'+scope+'|'+event
    entry=dict(id='mi-dict-'+hashlib.sha256(key.encode()).hexdigest()[:14],product_name=name,date=date,
        granularity={4:'year',7:'month',10:'day'}[len(date)],market=scope,event=event,
        aliases=list(aliases),match=match,evidence=evidence,origin=origin)
    entries.append(entry)

def evidence(stem,needle,length=420):
    p=ROOT/stem;meta=read(p.with_suffix('.json'));t=compact(p.with_suffix('.txt').read_text());needle=compact(needle);i=t.index(needle)
    candidates=[q for q in p.parent.glob(p.name+'.*') if q.suffix!='.json' and hashlib.sha256(q.read_bytes()).hexdigest()==meta['sha256']]
    if not candidates:
        # Retain a transparent hash of the already archived extraction, never claim PDF bytes.
        cap=p.with_suffix('.txt');sha=hashlib.sha256(cap.read_bytes()).hexdigest();scope='archived_extracted_text'
    else:cap=candidates[0];sha=meta['sha256'];scope=meta.get('hash_scope','response_bytes')
    return dict(url=meta['url'],captured_at=meta['captured_at'],quote=t[i:i+length],
        sha256=sha,hash_scope=scope,capture_file=str(cap.relative_to(ROOT)),text_file=str(p.with_suffix('.txt').relative_to(ROOT)),
        source_type='official',publisher='xiaomi',verified=True,locator='官方归档正文；移除排版空白后精确定位')

def history():
    meta=next(x for x in [json.loads(l) for l in (OUT/'fetches.jsonl').read_text().splitlines()] if x['url']=='https://www.mi.com/about/history')
    d=read(OUT/'history-extracted.json')
    reviewed={
      '2023-04-18':['小米13 Ultra'], '2022-12-11':['小米13系列'], '2022-07-04':['小米12S系列'],
      '2021-12-28':['小米12系列'], '2021-03-29':['小米11 Pro','小米11 Ultra','小米MIX FOLD'],
      '2019-09-24':['小米MIX Alpha'], '2018-05-31':['小米8透明探索版'], '2017-07-26':['小米AI音箱'],
      '2016-10-25':['小米MIX'], '2016-07-27':['小米笔记本Air'], '2016-03-29':['米家压力IH电饭煲'],
      '2014-12-09':['小米空气净化器'], '2014-07-22':['小米手机4','小米手环1代'],
      '2014-05-15':['小米平板1代','小米电视2'], '2014-04-23':['小米路由器','小米路由器mini'],
      '2013-12-03':['小米移动电源'], '2013-09-05':['小米手机3','小米电视'], '2013-07-31':['红米手机'],
      '2012-11-14':['小米盒子'], '2012-08-16':['小米手机2','小米手机1S'], '2012-05-15':['小米手机青春版'],
      '2011-08-16':['第一代小米手机']}
    aliases={'小米手机4':['小米4'],'小米手机3':['小米3'],'小米手机2':['小米2'],'小米手机1S':['小米1S'],
             '小米MIX Alpha':['MIX Alpha'],'小米MIX':['小米 MIX'],'小米MIX FOLD':['Xiaomi MIX FOLD']}
    for year in d['data']:
      for y,months in year.items():
       for month,quotes in months.items():
        for q in quotes:
         m=re.match(r'(\d+)月(\d+)日',q)
         if not m:continue
         date=f'{y}-{int(m[1]):02}-{int(m[2]):02}'
         for name in reviewed.get(date,[]):
          if date=='2021-12-28' and '小米12系列发布' not in q:continue
          e={k:meta[k] for k in ['url','captured_at','sha256','capture_file']}
          e.update(quote=q,source_type='official',publisher='xiaomi',verified=True,locator=f'HTML 内嵌 about_history.data[{y}][{month}]',hash_scope='response_bytes',text_file=str((OUT/'history-extracted.json').relative_to(ROOT)))
          add(name,date,e,aliases.get(name,[]))

def existing():
    rows=read_baseline();byid={r['id']:r for r in rows}
    for c in read(ROOT/'data/official/release-dates.json')['candidates']:
      r=c['release']
      if r['source']!='official':continue
      for id in c.get('ids',[]):
       if id.startswith('CN:mi_cn:') and id in byid:
        e=dict(r['evidence']);e.update(publisher='xiaomi',verified=True)
        add(byid[id]['name'],r['date'],e,origin='existing_product_official',event=r.get('event','announcement'))

def read_baseline():return json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()))

def ir():
    def group(stem,date,needle,names,aliases=None):
      e=evidence(stem,needle,650)
      for name in names:add(name,date,e,(aliases or {}).get(name,[]))
    base='data/release-dates/round2/raw/'
    group(base+'mi-ir-17','2021-08-10','在2021年8月10日的發佈會上',['Xiaomi MIX 4','小米平板5系列','小米电视大师77”OLED','Xiaomi Sound','CyberDog'])
    group(base+'mi-ir-17','2021-05-26','2021年5月26日',['Redmi Note 10系列'])
    group(base+'mi-ir-28','2020-02','2020年2月，我們發佈了',['小米10','小米10 Pro'])
    group(base+'mi-ir-31','2018-10','我們僅分別於2018年10月及2018年12月底發佈',['小米MIX 3'])
    group(base+'mi-ir-31','2018-12','我們僅分別於2018年10月及2018年12月底發佈',['小米Play'])
    group(base+'mi-ir-31','2019-01','我們於2019年1月發佈',['Redmi Note 7'])
    group(base+'mi-ir-31','2019-02','小米9系列於2019年2月發佈',['小米9系列'])
    group(base+'mi-ir-08','2023-08','2023年8月，我們在中國大陸地區發佈新一代XiaomiMIXFold3',['Xiaomi MIX Fold 3'])
    group(base+'mi-ir-08','2023-08','2023年8月，我們在中國大陸地區發佈新一代仿生四足機器人',['CyberDog 2'])
    group(base+'mi-ir-08','2023-08','我們於2023年8月在中國大陸地區發佈RedmiK60至尊版',['Redmi K60 至尊版'])
    group(base+'mi-ir-08','2023-08','我們於2023年8月在中國大陸地區發佈高端智能電視',['Xiaomi TV S Pro 100”'],{'Xiaomi TV S Pro 100”':['小米电视 S Pro 100英寸']})
    group(base+'mi-ir-07','2023-03','2023年3月，我們在中國大陸地區推出RedmiNote12Turbo',['Redmi Note 12 Turbo','Redmi Note 12 Turbo 哈利·波特版'])
    group(base+'mi-ir-07','2023-04','2023年4月，我們發佈了小米電視大師86英寸MiniLED',['小米电视大师86英寸Mini LED'])
    group(base+'mi-ir-07','2023-04','2023年4月，我們推出XiaomiPad6系列',['Xiaomi Pad 6系列'])
    group(base+'mi-22q4-release','2022-07','我們分別於2022年7月和2022年8月在中國大陸發佈',['Xiaomi 12S Ultra'])
    group(base+'mi-22q4-release','2022-08','我們分別於2022年7月和2022年8月在中國大陸發佈',['Xiaomi MIX Fold 2'])
    group(base+'mi-22q4-release','2022-12','2022年12月，我們在中國大陸地區推出Redmi品牌首款無線充電機型',['Redmi K60','Redmi K60 Pro'])
    group(base+'mi-22q4-release','2022-12','2022年12月，我們發佈了小米電視EAPro86英寸',['小米电视 EA Pro 86英寸'])
    group(base+'mi-22q4-release','2022-12','2022年12月，我們推出XiaomiWatchS2智能手錶',['Xiaomi Watch S2','Xiaomi Buds 4'])
    group(base+'mi-22q4-release','2023-02','2023年2月，我們推出XiaomiBook12.4二合一',['Xiaomi Book 12.4 二合一'])
    doc='docs/release-dates-round2-20261103/evidence/'
    group(doc+'mi-25q1-release','2025-05','2025年5月，我們在中國大陸地區發佈旗艦手機產品',['Xiaomi 15S Pro'])
    group(doc+'mi-25q1-release','2025-04','2025年4月，我們在中國大陸地區推出',['Redmi Turbo 4 Pro'])
    group(doc+'mi-25q1-release','2025-05','2025年5月，我們發佈了一系列智能大家電產品',['米家空调Pro人感上出风1.5匹超一级能效','米家新风空调Pro人感双出风立式3匹超一级能效','米家冰箱Pro双系统法式平嵌508L','米家双区洗衣机Pro双洗烘10kg','Xiaomi Pad 7 Ultra'])
    group(doc+'mi-25q1-release','2025-05','2025年5月，我們正式發佈XiaomiWatchS4',['Xiaomi Watch S4 eSIM 15周年纪念版'])
    group(doc+'mi-ir-02','2025-02','2025年2月和2025年3月，我們相繼在中國大陸地區和海外市場發佈Xiaomi15Ultra',['Xiaomi 15 Ultra'])
    group(doc+'mi-ir-02','2024-11','2024年11月，我們在中國大陸地區推出RedmiK80系列',['Redmi K80系列'])
    group(doc+'mi-ir-02','2025-02','在2025年2月，我們推出米家中央空調Pro',['米家中央空调Pro'])
    group(doc+'mi-ir-02','2025-02','2025年2月，我們發佈XiaomiBuds5Pro',['Xiaomi Buds 5 Pro'])
    group(doc+'mi-ir-03-web','2025-09','2025年9月，我們發佈新一代智能旗艦手機Xiaomi17系列',['Xiaomi 17','Xiaomi 17 Pro','Xiaomi 17 Pro Max'])
    group(doc+'mi-ir-03-web','2025-10','2025年10月，我們發佈REDMIK90系列',['REDMI K90','REDMI K90 Pro Max'])
    group(doc+'mi-ir-03-web','2025-09','2025年9月發佈了米家三區洗衣機Pro滾筒10kg',['米家三区洗衣机Pro滚筒10kg','米家冰箱Pro微冰鲜双系统法式平嵌560L'])
    group('docs/xiaomi-series-expansion-20261104/evidence/official-mi-24q3','2024-10','2024年10月，我們發佈了新一代智能旗艦手機Xiaomi15系列',['Xiaomi 15系列'])
    group('docs/xiaomi-series-expansion-20261104/evidence/official-mi-24q3','2024-10','2024年10月，我們推出新一代XiaomiWatchS4和小米手環9Pro',['Xiaomi Watch S4','小米手环9 Pro'])

if __name__=='__main__':
    history();existing();ir()
    # Identical normalized product/date/market/event assertions collapse; aliases merge.
    unique={}
    for e in entries:
      if e['id'] not in unique:unique[e['id']]=e
      else:unique[e['id']]['aliases']=sorted(set(unique[e['id']]['aliases']+e['aliases']))
    write(OUT/'archive-entries.json',list(unique.values()))
    print('raw',len(entries),'dedup',len(unique))
