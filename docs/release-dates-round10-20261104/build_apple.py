"""Reviewed exact historical model groups; no dates inferred from model years.

Dates below were read from the captured availability statements. 'today' is
resolved only where the original article explicitly says available/shipping today.
A dated announcement alone never supplies an availability date.
"""
import json,pathlib,re,gzip
from bs4 import BeautifulSoup
from goodsdex.release_scope import displayable
ROOT=pathlib.Path(__file__).resolve().parent
rows=json.loads(gzip.decompress((ROOT/'baseline.json.gz').read_bytes()));byid={r['id']:r for r in rows}
articles=json.load(open(ROOT/'apple-paragraphs.json'));cs=[];reviews=[]
def review(ids,fragment,date,phrase,reason,market='US'):
 hits=[r for r in articles if fragment in r['url']]; assert len(hits)==1,(fragment,len(hits))
 a=hits[0];cap=json.load(open(a['capture']));paras=a['paragraphs']
 # The reviewer chooses a specific statement, not any generic 'available' hit.
 quotes=[p for p in paras if phrase.lower() in p.lower()];assert quotes,(fragment,phrase)
 q=min(quotes,key=len);assert re.search(r'available|availability|shipping|ships|arriv|on sale|deliver',q,re.I),(fragment,q)
 raw=gzip.open(cap['raw_file']).read();soup=BeautifulSoup(raw,'html.parser');full=' '.join(soup.get_text(' ',strip=True).split());assert q in full
 lines=pathlib.Path(cap['text_file']).read_text().splitlines();date_context=next((l for l in lines[:20] if re.fullmatch(r'[A-Z][a-z]+ \d{1,2}, \d{4}',l)),None)
 assert date_context,(fragment,lines[:8])
 # Preserve the original dated dateline and exact generation/size context too.
 dated=next((p for p in paras if re.search(r'(?:CUPERTINO|California|SAN FRANCISCO)',p) and re.search(r'20\d\d',p)),None)
 support=[date_context]+([dated] if dated and dated!=q else [])
 availability_quotes=list(dict.fromkeys(p for p in paras if re.search(r'available|availability|shipping|ships|arriv|on sale|deliver',p,re.I)))
 keys=['GLOBAL:apple_support:model:'+str(i) for i in ids]
 kept=[]
 for key in keys:
  row=byid[key]
  if displayable(row.get('release')) or (row.get('release') or {}).get('source')=='official':continue
  kept.append(key)
 if not kept:return
 for key in kept:
  row=byid[key]
  e={k:cap[k] for k in ('url','sha256','captured_at')};e.update(quote=q,supporting_quotes=support,availability_quotes=availability_quotes,identity_quotes=[p for p in paras if re.search(r'\b(?:11|13|15|17|21.5|27)[-‑ ]inch|Thunderbolt|Touch Bar|generation|Retina|Wi-Fi',p)][:8],locator='Newsroom正文/Pricing & Availability；原文日期上下文单列，today仅在明确available/shipping时解读',source_type='official',capture_type='http_response',capture_file=cap['raw_file'],text_file=cap['text_file'],verified=True)
  cs.append(dict(family='round10:'+key,ids=[key],name=row['name'],brand='Apple',method='official_newsroom_availability',identity_review=reason,capture_file=cap['raw_file'],release=dict(date=date,event='availability',market=market,source='official',confidence='high',granularity='month',retrospective=True,evidence=e)))
 reviews.append(dict(ids=kept,date=date,url=cap['url'],reason=reason,quote=q,date_context=date_context))

# Exact generations of historical support models, not current buy-page SKUs.
review([112445],'2007/06/26Apple-and-AT-T','2007-06','iPhone goes on sale','初代iPhone，4/8GB；原文明确June29，美国首销')
review([112496],'2008/06/09Apple-Introduces-the-New-iPhone-3G','2008-07','iPhone 3G will be available','iPhone3G精确世代；原文July11，美国首销')
review([112307],'2009/06/08Apple-Announces-the-New-iPhone-3GS','2009-06','iPhone 3GS will be available','iPhone3GS精确世代；原文June19')
review([112562],'2010/09/19iPhone-4-Available-in-China','2010-09','will be available to customers in China','iPhone4精确世代；明确中国September25；不回填美国首销', 'CN')
review([112004],'2012/01/04iPhone-4S-Arrives-in-China','2012-01','will be available in China','iPhone4S精确世代；明确中国January13', 'CN')
review([112016],'2012/11/30iPad-mini-iPhone-5-Arrive-in-China','2012-12','iPhone® 5 will be available','iPhone5精确世代；正文December14中国上市', 'CN')
review([111917,111973],'2013/09/16iPhone-5s-iPhone-5c-Arrive','2013-09','will be available','iPhone5s及5c精确两型号，原文明列中国首发September20', 'CN')
review([111940,111954],'2014/09/30iPhone-6-iPhone-6-Plus-Available-in-China','2014-10','will be available in China beginning Friday, October 17','6和6Plus两精确型号，中国October17，未使用September全球上市月', 'CN')
review([111952,111996],'2015/09/21iPhone-6s-iPhone-6s-Plus-Arrive','2015-09','will be available at 8:00','6s和6sPlus精确型号，正文中国September25', 'CN')
review([111943,111953],'2016/09/apple-introduces-iphone-7-iphone-7-plus','2016-09','will be available in more than 25 countries beginning Friday, September 16','7和7Plus精确型号；地区段明确中国September16', 'CN')
review([112005],'2016/03/21Apple-Introduces-iPhone-SE','2016-03','availability beginning Thursday, March 31','SE初代；正文March31含中国；未匹配2020/2022代','CN')
review([111855],'2016/12/apple-airpods-are-now-available','2016-12','available to order online now','初代AirPods，原文December13及nowavailable；美国发售，非原9月预计上市')
review([111861],'2019/10/apple-reveals-new-airpods-pro-available-october-30','2019-10','in stores beginning Wednesday, October 30','初代AirPodsPro配无线充电盒；不传播2021MagSafe重发版')
review([111994],'2018/01/homepod-arrives-february-9','2018-02','arrives in stores beginning Friday, February 9','初代HomePod；原文明确US/UK/Australia；非中国上市')
review([111984],'2018/09/iphone-xs-iphone-xs-max-and-apple-watch-series-4-arrive-in-stores','2018-09','went on sale at 8 a.m.','Series4原文上市回顾；美国市场')
review([111891],'2017/09/apple-watch-series-3-with-cellular-now-available','2017-09','went on sale around the world at 8 a.m.','Series3首销回顾，非发布会时间')
review([111985,112022],'2016/09/apple-introduces-apple-watch-series-2','2016-09','beginning Friday, September 16','Series1与Series2精确型号；排除Nike/Hermès另行上市日期')
review([111918],'2020/09/apple-watch-series-6-delivers-breakthrough-wellness-and-fitness-capabilities','2020-09','availability beginning Friday, September 18','Series6及SE初代，各自明确September18美国上市')
# iPad: original model-level support identities, never inherit into capacity SKUs.
review([112438],'2010/03/05iPad-Available-in-US-on-April-3','2010-04','Wi-Fi + 3G models in late April','初代iPad；WiFi April3与3G lateApril同月，仅美国')
review([111990],'2011/03/10iPad-2-Arrives-Tomorrow','2011-03','will be available tomorrow at 5 p.m.','iPad2：原文March11及WiFi/3G两版本美国上市')
review([111992],'2012/03/14New-iPad-Arrives-in-the-US','2012-03','will arrive at Apple','iPad第三代，原文thirdgeneration及March16美国上市')
review([111978,111993],'2012/10/23Apple-Introduces-iPad-mini','2012-11','iPad mini with Wi-Fi models will be available','mini初代与iPad第四代精确型号，明确November2；型号参考，不匹配购买SKU')
review([112019],'2013/11/12iPad-mini-with-Retina-Display-Available','2013-11','is available starting today','mini2精确Retina代，原文November12availabletoday')
review([112020],'2013/10/23Apple-Announces-iPad-Air','2013-11','starting on Friday, November 1','iPadAir初代；美国November1，非October23发布日期')
review([112017,112018],'2014/10/16Apple-Introduces-iPad-Air-2','2014-10','will be available starting later next week','iPadAir2及mini3；原文October16、nextweek明确销售交付，月内；不当作October16当天开售')
review([112024],'2015/11/09Epic-12-9-inch-iPad-Pro','2015-11','is available to order online on Wednesday, November 11','12.9寸iPadPro初代，明确11月该周开售')
review([111965],'2016/03/21Apple-Introduces-9-7-inch-iPad-Pro','2016-03','in Apple’s retail stores, through select carriers and Apple Authorized Resellers on Thursday, March 31','9.7寸iPadPro，不混12.9寸；原文March31')
review([111960],'2017/03/new-9-7-inch-ipad','2017-03','starts delivering to customers and arriving next week','iPad第五代：A9、9.7寸与支持页一致；2017March21原文次周交付，仍为3月')
review([111977,118452],'2020/03/apple-unveils-new-ipad-pro-with-lidar-scanner','2020-03','available in stores starting next week','2020代12.9寸第四代、11寸第二代，LiDAR/A12Z型号匹配；原文3月18日次周实体上市')
# Macs: review exact year, size, CPU generation and port/touch-bar variants.
review([112553],'2007/08/07Apple-Unveils-New-iMac','2007-08','new iMac line is available immediately','2007中iMac铝壳、20/24寸与Core2Duo；明确立即供货')
review([112308],'2008/01/08Apple-Introduces-New-Mac-Pro','2008-01','new Mac Pro is shipping today','2008初MacPro，双四核Xeon；明确shippingtoday')
review([112467],'2008/02/26Apple-Introduces-New-MacBook-and-MacBook-Pro','2008-02','new MacBook and MacBook Pro models are now shipping','2008初MacBook塑料壳2.1/2.4GHz，非2008末铝壳')
review([112494],'2008/04/28Apple-Updates-iMac','2008-04','new iMac line is available immediately','2008初iMac，1066MHz总线及20/24寸完整规格核对')
review([112512],'2008/10/14New-MacBook-Family','2008-10','are now shipping','2008末铝壳13寸MacBook明确nowshipping；Air另为earlyNovember，未传播')
review([112590],'2009/03/03Apple-Introduces-New-Mac-Pro','2009-03','new Mac Pro will be available next week','2009初MacPro，NehalemXeon；3月3日nextweek仍3月')
review([111345,112427],'2009/03/03Apple-Updates-Consumer-Desktop-Line','2009-03','new iMac and Mac mini lines are now shipping','2009初iMac/Macmini，NVIDIA9400M型号核对；明确nowshipping')
review([112473,112474,112624],'2009/06/08Apple-Updates-MacBook-Pro-Family','2009-06','13-inch MacBook Pro, 15-inch MacBook Pro, 17-inch MacBook Pro and MacBook Air are now available','2009中13/15/17寸、含15寸2.53GHz；明确nowshipping')
review([112565,112482],'2009/10/20Apple-Unveils-New-iMac','2009-10','Intel Core 2 Duo iMac and Mac mini lines are now shipping','2009末21.5寸Core2Duo iMac与Macmini明确nowshipping；27寸跨10/11月配置不唯一、MacBook需另页，未写入')
review([112604,112605,112606],'2010/04/13Apple-Updates-MacBook-Pro-Line','2010-04','new 13-inch MacBook Pro, 15-inch MacBook Pro, and 17-inch MacBook Pro are now available','2010中13/15/17寸MBP；供货段明确today')
review([112588,112589],'2010/06/15Apple-Unveils-All-New-Mac-mini','2010-06','new Mac mini is shipping today','2010中Macmini与Server，正文配置含两款，明确shippingtoday')
review([112566,112567],'2010/07/27Apple-Updates-iMac-Line','2010-07','new iMac line is shipping now','2010中21.5/27寸iMac，供货段及配置核对')
review([112578],'2010/07/27Apple-Unveils-New-Mac-Pro','2010-08','will be available in August','2010中MacPro，原文August供货；不用July发布月')
review([112580,112585],'2010/10/20Apple-Reinvents-Notebooks','2010-10','MacBook Air are immediately available','2010末11/13寸Air，明确供货today')
review([112006,112007],'2011/07/20Apple-Updates-Mac-mini','2011-07','in stores tomorrow','2011中Macmini/Server，正文含Server双盘配置；明确availabletoday')
review([112038,112439],'2011/07/20Apple-Updates-MacBook-Air','2011-07','starting July 21','2011中11/13寸Air；7月21日实体供货，非7月20日预订')
review([111926,112012],'2012/10/23All-New-iMac-Features','2012-10','Mac mini is available today','2012末Macmini与Server，配置逐项明确，供货today')
review([112435],'2012/11/27iMac-Available-on-November-30','2012-11','will be available on Friday, November 30','2012末21.5寸iMac，11月30日供货')
review([112433],'2012/11/27iMac-Available-on-November-30','2012-12','will begin shipping in December','2012末27寸iMac，明确December；不继承21.5寸November')
review([118465,118466],'2013/02/13Apple-Updates-Processors-Prices-of-MacBook-Pro','2013-02','are available today','2013初13/15寸RetinaMBP，2.6GHz/2.4GHz处理器新款；不继承原2012代')
review([111938,112437],'2013/06/10Apple-Brings-All-Day-Battery-Life','2013-06','are available today','2013中11/13寸Air，Haswell型号对应')
review([111967,111970],'2013/09/24Apple-Updates-iMac','2013-09','new iMac is available today','2013款21.5/27寸iMac，第四代Intel对应')
review([111946,111971],'2013/10/23MacBook-Pro-with-Retina','2013-10','MacBook Pro with Retina display is available today','2013末13/15寸Retina，Haswell/Thunderbolt2完整世代匹配')
review([112025],'2013/12/18All-New-Mac-Pro-Available','2013-12','will be available to order starting Thursday, December 19','2013末圆筒MacPro；12月18日原文明说次日供货')
review([111944,112032],'2014/04/29Apple-Updates-MacBook-Air','2014-04','MacBook Air is available today','2014初11/13寸Air，1.4GHz配置核对')
review([112031],'2014/06/18Apple-Introduces-New-Entry-Level','2014-06','new 21.5-inch iMac is available today','2014中21.5寸入门iMac，1.4GHz双核匹配')
review([111935,111942],'2014/07/29Apple-Updates-MacBook-Pro','2014-07','are available today','2014中13/15寸RetinaMBP，供货today')
review([112436],'2014/10/16Apple-Introduces-27-inch-iMac','2014-10','begins shipping today','2014末27寸Retina5KiMac初代，明确shippingtoday')
review([111931],'2014/10/16Apple-Updates-Mac-mini','2014-10','Mac mini begins shipping today','2014末Macmini，Intel第四代，明确shippingtoday')
review([111956,112441,111959],'2015/03/09Apple-Updates-13-inch-MacBook-Pro','2015-03','available today','2015初11/13Air及13寸RetinaMBP，处理器/ForceTouch核对')
review([112442],'2015/03/09Apple-Unveils-All-New-MacBook','2015-04','will begin shipping Friday, April 10','2015初12寸RetinaMacBook；4月10日发售，非3月发布月')
review([111955,112434],'2015/05/19Apple-Introduces-15-inch-MacBook-Pro','2015-05','is available today','2015中15寸RetinaMBP与27寸5KiMac，ForceTouch/入门5K配置分别核对')
review([112034,112035,112036],'2015/10/13Apple-Updates-iMac-Family','2015-10','is available today','2015末21.5寸非Retina/4K与27寸5K，正文三配置核对')
review([111999],'2016/10/apple-unveils-groundbreaking-new-macbook-pro','2016-10','and ships today','2016末13寸两Thunderbolt端口、非TouchBar；同页TouchBar版2-3周后，绝不套用')
review([111921,111924,111947,111951,111969,111972,111986,112026],'2017/06/imac-receives-major-update','2017-06','available to buy in Apple Stores starting on Wednesday, June 7','2017代iMac21.5/4K/5K、13Air、12MacBook及13/15MBP；独立逐行规格对照，第7代Intel；有明确6月7日供货')
review([111995],'2017/12/imac-pro-the-most-powerful-mac-ever','2017-12','is available on December 14','2017iMacPro，12月14日明确销售回顾')
review([111941,111997],'2019/05/apple-introduces-first-8-core-macbook-pro','2019-05','are available today','2019代13寸四端口TouchBar及15寸；不混两端口13寸7月机型')
review([111945,111948],'2019/07/macbook-air-and-macbook-pro-updated','2019-07','are available today','2019Air与入门13寸两端口MBP；参数TrueTone/T2/TouchBar核对')
review([111963,111998],'2019/03/imac-gets-a-2x-performance-boost','2019-03','in Apple Stores and through Apple Authorized Resellers next week','2019代21.5寸4K及27寸5K；实体下周交付也在3月')
review([111339,111981],'2020/05/apple-updates-13-inch-macbook-pro','2020-05','begin arriving to customers','2020代13寸四端口/两端口；正文10代/8代Intel明确区分，均5月8日交付')
review([111913],'2020/08/27-inch-imac-gets-a-major-update','2020-08','will begin arriving to customers','2020代27寸5KiMac，10代Intel；8月4日原文明确本周到货')

review([111862],'2020/09/apple-watch-se-the-ultimate-combination-of-design-function-and-value','2020-09','availability beginning Friday, September 18','SE初代精确型号，原文GPS/Cellular均9月18日美国发售')
review([112009,112010,112011],'2015/03/09Apple-Watch-Available-in-Nine-Countries-on-April-24','2015-04','will be available on Friday, April 24','首代Watch/Sport/Edition三款在正文分别列名；原文明确4月24日包括中国开售，非3月发布','CN')
review([112447],'2008/10/14New-MacBook-Family','2008-11','new MacBook Air will be available in early November','2008末Air明确earlyNovember；未采用同文MacBook的nowshipping十月')
review([112660],'2009/06/08Apple-Updates-MacBook-Pro-Family','2009-06','17-inch MacBook Pro and MacBook Air are now available','2009中MacBookAir 1.86/2.13GHz配置正文明确对应；供货段单独列出Air，非继承MBP')

(ROOT/'apple-reviewed-groups.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
(ROOT/'apple-new-candidates.json').write_text(json.dumps(cs,ensure_ascii=False,indent=2)+'\n')
print('Apple accepted rows',len(cs),'groups',len(reviews))
