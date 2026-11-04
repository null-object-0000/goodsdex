"""Frozen exact-identity review; captures reused, no research/network on replay."""
import json,re,sys,hashlib,gzip
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from goodsdex.release_scope import release_scope,displayable,scope_coverage
from goodsdex.third_party_release import apply_third_party,assess
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'baseline.json').read_text()) if (ROOT/'baseline.json').exists() else json.loads(gzip.decompress((ROOT/'baseline.json.gz').read_bytes()));byid={r['id']:r for r in rows}
captures={v['url']:v for p in (ROOT/'evidence').glob('*.json') for v in [json.loads(p.read_text())]}
def snippet(text,anchor,length=230):
 import unicodedata
 norm=lambda x:''.join(unicodedata.normalize('NFKC',x).split())
 chars=[];positions=[]
 for i,ch in enumerate(text):
  for c in norm(ch):chars.append(c);positions.append(i)
 n=''.join(chars);a=norm(anchor)
 if a not in n:raise ValueError('Missing anchor: '+anchor)
 i=positions[n.index(a)];return text[i:i+length]
def assertion(url,day,event,anchor,identity_anchor=None,upstream=None):
 v=captures[url];e={k:v[k] for k in ('url','sha256','captured_at')}
 e.update(quote=snippet(v['text'],anchor),locator='正文：'+anchor,source_type='third_party',
  identity_quote=snippet(v['text'],identity_anchor or anchor),identity_verified=True,event_verified=True)
 if upstream:e['upstream_origin']=upstream
 return dict(source='third_party',date=day,event=event,market='CN',evidence=e)
def add(key,assertions,reason):
 r=byid[key];assert release_scope(r)['tier']=='machine'
 assert not any(displayable(r.get(k)) for k in ('release','release_series')),key
 assert sum(x['name']==r['name'] for x in rows)==1,('ambiguous',key)
 cs.append(dict(id=key,name=r['name'],brand=r['brand'],identity_review=reason,assertions=assertions))
cs=[]
iromo='https://www.ithome.com/0/873/541.htm';mromo='https://news.mydrivers.com/1/1066/1066711.htm'
for key,model in [('192291','P'),('192351','P'),('192382','A'),('192411','A'),('192441','S'),('192471','S')]:
 add('CN:dji:sku:'+key,[assertion(iromo,'2025-08-06','announcement','大疆今晚发布了', 'ROMO '+model+'：'),assertion(mromo,'2025-08-06','announcement','快科技8月6日消息','DJI ROMO '+model+'：')],
  '两个原创媒体正文同日明确发布，分别列出P/A/S及水箱/自动上下水版本和对应定价；不继承基础机型。')
for key in ['231321','231741','232193','232251']:
 add('CN:dji:sku:'+key,[assertion('https://news.mydrivers.com/1/1121/1121522.htm','2026-05-11','announcement','快科技5月11日消息','DJI ROMO P2（水箱版）'),assertion('https://family.pconline.com.cn/2148/21480531.html','2026-05-11','announcement','5月11日','DJI ROMO P2水箱版')],
  'PConline原创编辑稿与快科技原创；原文明确5月11日及4款配置。6月11日开售是不同事件，不参与发布日冲突比较。')
add('CN:mi_cn:product:8152',[assertion('https://www.ithome.com/0/362/555.htm','2018-05-31','announcement','5⽉31⽇下午2点','小米8 SE 4GB+64GB版本'),assertion('https://news.mydrivers.com/1/579/579904.htm','2018-05-31','announcement','5月31日，小米在深圳发布小米8','6GB RAM+64GB ROM')], '精确小米8 SE 6GB+64GB；两稿明确配置和5月31日发布，6月8日开售不混用。')
add('CN:mi_cn:product:10000024',[assertion('https://www.ithome.com/0/260/817.htm','2016-09-27','announcement','IT之家讯','小米5s采用了高通'),assertion('https://news.mydrivers.com/1/501/501293.htm','2016-09-27','announcement','今天下午，小米小米5S/5S Plus正式和我们见面','小米5S回归金属机身',upstream='sina.com.cn')], '无容量限定的model_reference，精确5s，排除5s Plus；第二稿保留新浪开箱上游，独立于IT之家。')
add('CN:mi_cn:product:10000083',[assertion('https://www.ithome.com/0/330/181.htm','2017-10-16','announcement','IT之家 10月16日消息','红米5A配备2GB内存'),assertion('https://news.mydrivers.com/1/551/551987.htm','2017-10-16','announcement','非常突然，今天小米官方正式宣布发布','内置2GB内存和16GB')], '无容量限定的红米5A型号参考，两稿确认同名入门款，2+16原始版本，未套用后续配色。')
add('CN:mi_cn:product:7599',[assertion('https://www.ithome.com/0/345/528.htm','2018-01-29','announcement','IT之家1月29日消息','其中4c为1GB'),assertion('https://news.mydrivers.com/1/565/565010.htm','2018-01-29','announcement','如上周预告，1月29日上午','配备2GB+8GB')], '小米盒子4精确型号，白色2+8GB，排除4c/4S/SE；2月开售不与1月发布混用。')
for key in ['CN:byd:car:han:2023:dmi','CN:byd:car:han:2023:dmp']:
 add(key,[assertion('https://news.mydrivers.com/1/910/910685.htm','2023-05-18','announcement','5月18日，比亚迪汉DM-i冠军版','其中，汉DM-i冠军版'),assertion('https://www.ithome.com/0/694/151.htm','2023-05-18','announcement','IT之家 5 月 22 日消息','汉 DM-i 冠军版 / DM-p 战神版汽车上市 72 小时')],
  '逐trim核对2023 DM-i冠军版6配置/DM-p战神版1配置；不会仅凭2023年款匹配，也不扩到2024战神版。上市活动记announcement，无交付日证明。')
# Both same-name VR rows are deliberately not written: no unique identity mapping.
rejected=[]
for key in ['10000101','8202']:
 rejected.append(dict(id='CN:mi_cn:product:'+key,name=byid['CN:mi_cn:product:'+key]['name'],reason='型号无法唯一匹配：两个同名model_reference，无容量区分',assertions=[assertion('https://www.ithome.com/0/362/525.htm','2018-05-31','announcement','IT之家5月31日消息'),assertion('https://news.mydrivers.com/1/579/579196.htm','2018-05-31','announcement','5月31日，小米VR一体机')]))
rejected.append(dict(id='CN:dji:sku:142711',name=byid['CN:dji:sku:142711']['name'],reason='无可靠第三方交叉：两个事件不同；发布7月5日与开售报道7月6日不能互证',assertions=[assertion('https://www.ithome.com/0/807/056.htm','2023-07-05','announcement','大疆 Osmo Mobile 6 手机云台浅银灰配色版发布于'),assertion('https://jd.zol.com.cn/824/8244600.html','2023-07-06','availability','大疆的手机云台一直')]))
# HP full SKU lookup returned no exact release news; configuration aliases collide.
for key in ['DK8G8PA','E5HR5PA']:
 r=byid['CN:hp_cn:sku:'+key]
 rejected.append(dict(id=r['id'],name=r['name'],reason='型号无法唯一匹配：同CPU/内存/容量的不同货号，媒体仅系列配置且预告/正式发布语义不同',assertions=[assertion('https://www.ithome.com/0/944/661.htm','2026-04-28','announcement','IT之家 4 月 28 日消息','Ultra 5 225H + 16GB + 512GB'),assertion('https://news.pconline.com.cn/2140/21407771.html','2026-04-28','announcement','4月28日消息','Ultra 5 225H+16GB+512GB')]))
out=Path('data/third-party/release-dates.json');out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(dict(schema=1,policy='two-independent-originals-exact-event-day-v1',candidates=cs),ensure_ascii=False,indent=2)+'\n')
(ROOT/'rejected-reviewed.json').write_text(json.dumps(rejected,ensure_ascii=False,indent=2)+'\n')
for c in cs:
 assert assess(c['assertions'])['status']=='corroborated'
print('candidates',len(cs),Counter(c['brand'] for c in cs),'rejected',len(rejected))
