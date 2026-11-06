"""Assemble manually reviewed exact-product assertions, using existing two-origin gate."""
from copy import deepcopy
from pathlib import Path
import gzip,hashlib,json,re,sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
sys.path.insert(0,str(REPO/'src'))
from goodsdex.third_party_release import assess
from goodsdex.release_dates import validate

def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
captures={c['url']:c for p in (ROOT/'evidence').glob('*.json') if (c:=read(p))}
# Dates are event dates stated in the original prose; publication time supplies year context.
# No series propagation. H501 announcement replaces the displayed event, not its historical sale audit.
specs=[
 ('20833','2024-12-24','availability',[
 ('https://www.ithome.com/0/819/782.htm','IT之家 12 月 24 日消息','据介绍'),
 ('https://news.mydrivers.com/1/1021/1021233.htm','快科技12月24日消息','米家智能宠物饮水机2最大优势')]),
 ('20981','2025-02-27','announcement',[
 ('https://www.ithome.com/0/834/163.htm','IT之家 2 月 27 日消息','小米智能音箱 Pro 支持'),
 ('https://news.mydrivers.com/1/1032/1032928.htm','快科技2月27日消息','这款智能音箱')]),
 ('20807','2024-12-03','availability',[
 ('https://www.ithome.com/0/814/907.htm','IT之家 12 月 3 日消息','外观方面'),
 ('https://news.mydrivers.com/1/1017/1017300.htm','快科技12月3日消息','先看外观')]),
 ('19409','2023-11-10','availability',[
 ('https://www.ithome.com/0/731/506.htm','小米智能门锁 2 发布于 11 月 7 日','下单赠送'),
 ('https://news.mydrivers.com/1/944/944233.htm','快科技11月7日消息','小米智能门锁2采用')]),
 ('20276','2024-08-16','availability',[
 ('https://www.ithome.com/0/788/888.htm','IT之家 8 月 16 日消息','小米 BE6500 路由器采用'),
 ('https://news.mydrivers.com/1/997/997689.htm','快科技8月16日消息','BE6500支持')]),
 ('18520','2023-05-25','announcement',[
 ('https://jd.zol.com.cn/818/8187764.html','5 月 25 日消息','米家高速吹风机 H501 主打'),
 ('https://news.mydrivers.com/1/912/912258.htm','快科技5月25日消息','据介绍')]),
 ('19332','2023-10-31','availability',[
 ('https://www.ithome.com/0/728/923.htm','IT之家 10 月 31 日消息','IT之家整理'),
 ('https://news.mydrivers.com/1/942/942944.htm','最近，小米推出了','购买链接')]),
 ('10015','2019-06-18','availability',[
 ('https://www.ithome.com/0/427/660.htm','小爱音箱支持人工智能语音对话','支持一句话遥控'),
 ('https://news.mydrivers.com/1/631/631847.htm','6月17日消息','小米智能硬件部总经理')]),

]
import subprocess
rows=json.loads(gzip.decompress(subprocess.check_output(['git','show','2cd5f4173b420a8c51b674a293313f544233f4e7:public/goods.json.gz'],cwd=REPO)))
byid={r['id']:r for r in rows};new=[]
for pid,day,event,sources in specs:
    key='CN:mi_cn:product:'+pid;row=byid[key];assertions=[]
    for url,start,end in sources:
        c=captures[url];assert c['status']==200
        raw=gzip.decompress(Path(c['raw_file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==c['sha256']
        t=re.sub(r'\s+',' ',Path(c['text_file']).read_text()).strip()
        i=t.index(start);j=t.index(end,i+len(start));quote=t[i:j].strip()
        assert len(quote)<2200,(pid,len(quote))
        e={k:c[k] for k in ('url','sha256','captured_at')}
        e.update(quote=quote,locator='article/body; publication year + explicit event sentence',source_type='third_party',capture_type='http_response',capture_file=c['raw_file'],text_file=c['text_file'],identity_quote=quote,identity_verified=True,event_verified=True,published_at=re.search(r'20\d{2}[-/]\d{1,2}[-/]\d{1,2}',t).group(),upstream_origin='zol.com.cn' if 'zol.com.cn' in url else 'ithome.com' if 'ithome.com' in url else 'mydrivers.com')
        assertions.append(dict(source='third_party',date=day,event=event,market='CN',evidence=e))
    assert assess(assertions)==dict(status='corroborated',delta_days=0,display_allowed=True)
    new.append(dict(id=key,name=row['name'],brand=row['brand'],review_batch='user-items-20261106',identity_review='精确单品；两个不同作者/媒体的自有原文，未见相互转载或共享稿源署名；不把型号近似或系列日期作为证据',assertions=assertions))
# Record all input assertions in the existing canonical candidate file; the media sidecar
# is also required by apply_release_dates -> apply_third_party (no gate changes).
official_path=REPO/'data/official/release-dates.json';official=read(official_path)
existing={i for c in official['candidates'] for i in c['ids']}
for c in new:
    if c['id'] in existing and not c['id'].endswith(':18520'):continue
    a=c['assertions'][0]
    candidate=dict(family='user-items-20261106:'+c['id'],ids=[c['id']],name=c['name'],method='explicit_third_party_date',release=dict(date=a['date'][:7],granularity='month',source='third_party',level='product',confidence='medium',event=a['event'],market='CN',evidence=deepcopy(a['evidence'])))
    if c['id'].endswith(':18520'):
        old=next(x for x in official['candidates'] if c['id'] in x['ids'])
        if not (ROOT/'h501-superseded-candidate.json').exists():write(ROOT/'h501-superseded-candidate.json',old)
        candidate['release']['previous_release']=deepcopy(byid[c['id']]['release'])
        official['candidates']=[x for x in official['candidates'] if c['id'] not in x['ids']]
    validate(candidate);official['candidates'].append(candidate)
# Official exact-kit price announcement. Capture is the browsing tool's page text,
# not the separate curl 403 response. The June forecast is NOT asserted as a sale.
kit_id='CN:fuji:kit:x-s20-16-50mm'
capfile=ROOT/'evidence/fuji-official-web.txt.gz';raw=gzip.decompress(capfile.read_bytes());text=raw.decode()
url='https://newsroom-us.fujifilm.com/press-releases/press-release-details/2024/Calling-All-Creatives-Fujifilm-Announces-FUJIFILM-X-T50-Mirrorless-Digital-Camera-and-FUJINON-XF16-50mmF2-8-4-8-R-LM-WR-Lens-05-16-2024/default.aspx'
quote='FUJIFILM X-S20 with XF16-50mmF2.8-4.8 R LM WR Lens Kit: MSRP $1,699.95 USD ($2,299.99 CAD)'
assert quote in text and '05/16/2024' in text
assert byid[kit_id]['params']['含镜头']=='XF16-50mmF2.8-4.8 R LM WR'
kit=dict(family='user-items-20261106:'+kit_id,ids=[kit_id],name=byid[kit_id]['name'],method='official_retrospective',identity_review='美国官方2024-05-16新闻稿单独公布X-S20 + XF16-50完整套机及价格；只记套机公布月份，未继承2023机身日期，未把预计6月作为实际首销',release=dict(date='2024-05',granularity='month',source='official',level='product',confidence='high',event='announcement',market='US',retrospective=True,evidence=dict(url=url,quote=quote,date_context='05/16/2024',locator='U.S. Newsroom / publication date + Pricing and Availability / exact X-S20 kit price bullet',sha256=hashlib.sha256(raw).hexdigest(),captured_at=datetime.fromtimestamp(capfile.stat().st_mtime,timezone.utc).isoformat(),source_type='official',capture_type='web_tool_page_text',capture_file=str(capfile.relative_to(REPO)),text_file=str((ROOT/'evidence/fuji-official-web.txt').relative_to(REPO)),verified=True)))
validate(kit)
official['candidates']=[c for c in official['candidates'] if kit_id not in c['ids']]+[kit]
write(ROOT/'new-official-candidate.json',kit)
write(official_path,official)
media_path=REPO/'data/third-party/release-dates.json';media=read(media_path)
media['candidates']=[c for c in media['candidates'] if c.get('review_batch')!='user-items-20261106']
assert not ({c['id'] for c in media['candidates']}&{c['id'] for c in new})
media['candidates'].extend(new);write(media_path,media)
write(ROOT/'new-media-candidates.json',new)
print('reviewed media products',len(new),'official exact-kit announcements',1)
