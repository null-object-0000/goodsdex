"""Manual evidence-backed verdicts keyed to the frozen review queue."""
import json
from datetime import datetime,timezone
from pathlib import Path
P=Path(__file__).resolve().parent
V={}
def add(family,date,url,note,supported=False,evidence_file=None):
    V[family]=dict(correct_date=date,verification_url=url,verification_note=note,original_evidence_supported=supported,evidence_artifact=evidence_file)
add('Apple|平板|ipad（第9代)', '2021-09', 'https://www.apple.com/uk/newsroom/2021/09/apples-most-popular-ipad-delivers-even-more-performance-and-advanced-features/', '官方9月14日发布第9代；原URL本次cache miss，未核实原引文。',None,'apple-web-7.json')
add('Apple|手机|iphone4s','2011-10','https://www.apple.com/newsroom/2011/10/04Apple-Launches-iPhone-4S-iOS-5-iCloud/','官方10月4日发布；模型原URL缺少-iOS-5-iCloud，实读404。',False,'apple-web-2.json')
add('Apple|手机|iphone6plus','2014-09','https://www.apple.com/mu/newsroom/2014/09/09Apple-Announces-iPhone-6-iPhone-6-Plus-The-Biggest-Advancements-in-iPhone-History/','官方9月9日同时发布6与6 Plus；模型原Unveils URL为404。',False,'apple-web-2.json')
add('Apple|手表|applewatchseries2','2016-09','https://www.apple.com/newsroom/2016/09/apple-introduces-apple-watch-series-2/','官方9月7日发布Series 2；原URL被搜索索引抓取，正文支持型号与月份。',True,'apple-web-2.json')
add('Apple|电脑|macmini(2007年中)','2007-08','https://www.informaticanapoli.it/download/MANUALI/APPLE/mac_mini_early_late_06.pdf','Apple原厂维修手册存档第7页记录Mid 2007于August 2007换Core 2 Duo；原新闻稿URL未核实，不用事后来源替换原证据。',None,'apple-web-4.json')
add('Apple|电脑|macbook（13英寸，2009年末机型）','2009-10','https://www.apple.com/newsroom/2009/10/20Apple-Updates-MacBook-With-LED-Backlit-Display-Multi-Touch-Trackpad-Built-in-Seven-Hour-Battery/','官方10月20日发布白色unibody 13.3英寸MacBook；模型自己承认原support页不支持月份，原页抓取429。',False,'apple-web-3.json')
add('Apple|手机|iphone3gs','2009-06','https://www.apple.com/uk/newsroom/2009/06/08Apple-Announces-the-New-iPhone-3GS-The-Fastest-Most-Powerful-iPhone-Yet/','官方6月8日发布3GS；模型原Introduces短URL未核实。',None,'apple-web-5.json')
add('Apple|平板|ipadmini3','2014-10','https://www.apple.com/cl/environment/pdf/products/archive/2014/iPadmini3_PER_oct2014.pdf','原厂mini3环境报告标明2014年10月16日，官方Air2新闻稿亦点名mini3；原短URL404。',False,'apple-web-4.json')
add('Apple|电脑|macbookpro(retina,13英寸,2013年初机型)','2013-02','https://www.apple.com/newsroom/2013/02/13Apple-Updates-Processors-Prices-of-MacBook-Pro-with-Retina-Display/','官方2月13日更新13英寸Retina MBP；模型原support/112009实际为Apple Watch一代规格页，错引产品。',False,'apple-web-3.json')
add('Apple|电脑|imac(2009年初机型)','2009-03','https://www.apple.com/newsroom/2009/03/03Apple-Updates-Consumer-Desktop-Line/','官方3月3日更新iMac；模型原support/112010实际为Apple Watch Sport一代规格页，错引产品。',False,'apple-web-4.json')

add('大疆|云台|如影ronin2','2017-04','https://www.prnewswire.com/news-releases/dji-introduces-ronin-2-a-more-powerful-versatile-and-intelligent-stabilizer-for-film-and-video-professionals-300443974.html','DJI自行发出的4月23日新闻稿；原短URL未能读取，未核实原依据。',None,'dji-web-1.json')
add('大疆|影像传输与控制设备配件|djifocusprolidar','2024-04','https://www.mynewsdesk.com/uk/dji/pressreleases/dji-pro-launches-next-generation-tools-offering-swift-setup-intuitive-operation-seamless-integration-and-extended-focus-control-3315434','DJI原厂4月9日稿及组件Product Information同时点名LiDAR；原短URL不可访问，未核实原依据。',None,'dji-web-5.json')
add('大疆|相机|djironin4d-8k基础版','2021-10','https://www.mynewsdesk.com/uk/dji/pressreleases/dji-revolutionizes-filmmaking-with-worlds-first-4-axis-cinema-camera-3137828','按prompt的型号世代首次announcement：2021年10月20日原厂已同时宣布8K/6K combos；8K实际上市稿是2023年12月，均不支持2023-10。原规格页不能证明首次月份。',False,'dji-web-5.json')
add('大疆|相机|djironin4d-6k','2021-10','https://www.mynewsdesk.com/uk/dji/pressreleases/dji-revolutionizes-filmmaking-with-worlds-first-4-axis-cinema-camera-3137828','原厂2021年10月20日明确6K combo；模型只给产品页无首次月份引文，未核实原依据。',None,'dji-web-5.json')
add('大疆|影像传输与控制设备配件|djifocuspro手轮','2024-04','https://www.dji.com/focus-pro/downloads','手轮Product Information日期2024-04-09，并由同日原厂发布稿点名；模型原产品页无月份原句，未核实。',None,'dji-web-3.json')
add('大疆|无人机配件|djiair3系列充电管家','2023-07','https://www.dji.com/air-3/video','官方视频目录2023-07-25已单列Battery Charging Hub，原厂同日Air3稿配套发布，非单借主机；模型承认原依据未找到配件首次月份。',False,'dji-web-5.json')
add('大疆|云台|osmomobile6','2022-09','https://www.dji.com/media-center/announcements/dji-osmo-mobile-6-pushes-smartphone-photography-further','官方2022-09-22发布Mobile6；模型原产品页无月份引文，未核实原依据。',None,'dji-web-3.json')
add('大疆|摄影器材配件|djilidar焦点测距器','2021-10','https://www.mynewsdesk.com/uk/dji/pressreleases/dji-revolutionizes-filmmaking-with-worlds-first-4-axis-cinema-camera-3137828','商品vid111651官方商城定位Ronin4D配件，原厂2021-10稿明确LiDAR focusing system；月份相符，但模型reason错称2020年RS2配件，证据链不合格。',False,'dji-web-5.json')
add('大疆|无人机|djimatrice4t','2025-01','https://www.dji.com/media-center/announcements/matrice-4-series','官方2025-01-08稿同时点名4T/4E；原系列产品页无月份引文，未核实。',None,'dji-web-2.json')
add('大疆|摄影器材配件|djircpro','2021-11','https://www.dji.com/uk/newsroom/news/dji-mavic-3-release','官方2021-11-05发布Mavic3且明确包含RC Pro，RC Pro下载页同日首次产品文档；候选2021-10错误。',False,'dji-web-2.json')

add('富士|相机|fujifilmx100vi','2024-02','https://www.fujifilm.com/us/en/news/digital-cameras/fujifilm-debuts-x100vi-mirrorless-digital-camera','原厂2024-02-20公告；日本3月上市不能替代全球2月公告。模型原产品页仅回指型号，原月份依据未核实。',None,'fuji-web-1.json')
add('富士|相机镜头|xf10-24mmf4roiswr','2020-10','https://www.fujifilm-x.com/en-ph/news/fujifilm-introduces-fujinon-xf10-24mmf4-r-ois-wr-lens/','原厂2020-10-15明确WR更新版，非2013非WR旧款；原产品页月份未核实。',None,'fuji-web-1.json')
add('富士|相机镜头|xf100-400mmf4.5-5.6rlmoiswr','2016-01','https://fujifilm-korea.co.kr/support/notice/id/7193?p=27','原厂2016-01-15发布，2月为上市；原产品页月份未核实。',None,'fuji-web-4.json')
add('富士|相机镜头|xf80mmf2.8rlmoiswrmacro','2017-09','https://fujifilm-korea.co.kr/support/notice/id/7251','原厂页面2017-09-07公告11月上市，按announcement取9月；原产品页月份未核实。',None,'fuji-web-6.json')
add('富士|相机镜头|xf150-600mmf5.6-8rlmoiswr','2022-05','https://www.fujifilm-x.com/en-gb/news/fujifilm-announces-fujinon-xf150-600mmf5-6-8-r-lm-ois-wr/','原厂2022-05-31正式公告7月上市；原产品页月份未核实。',None,'fuji-web-5.json')
add('富士|相机镜头|xc50-230mmf4.5-6.7oisii','2015-01','https://www.dpreview.com/articles/9503379114/fujifilm-unveils-fujinon-xc16-50mm-ii-and-xc50-230mm-ii-kit-lenses-for-x-a2/','内嵌FUJIFILM原厂2015-01-15新闻稿明确II代。date给2015-01同时abstention_reason自称date=null，保留实际字段按日期候选，原依据自称不足。',False,'fuji-web-6.json')
add('富士|相机|fujifilmx-s20','2023-05','https://www.fujifilm.com/ae/en/news/hq/9421','原厂2023-05-24公告6月29日上市；原产品页月份未核实。',None,'fuji-web-5.json')
add('富士|相机镜头|xf18-120mmf4lmpzwr','2022-05','https://www.fujifilm-x.com/fr-fr/news/fujifilm-annonce-le-fujinon-xf18-120mmf4-lm-pz-wr/','原厂2022-05-31已正式公告9月上市，不是仅开发路线图；模型2022-09混淆上市与announcement。',False,'fuji-web-3.json')
add('富士|相机镜头|xf55-200mmf3.5-4.8rlmois','2013-04','https://www.mynewsdesk.com/se/fujifilm-nordic/pressreleases/launch-of-the-first-telephoto-zoom-for-the-xf-lens-series-fujinon-xf55-200mmf3-5-4-8-r-lm-ois-856842','FUJIFILM Nordic原厂新闻稿2013-04-17明确该镜头；原产品页月份未核实。',None,'fuji-web-4.json')
add('富士|相机镜头|xf27mmf2.8rwr','2021-01','https://www.fujifilm-x.com/en-in/news/fujifilm-announces-new-fujinon-xf27mmf2-8-r-wr-lens/','原厂2021-01-27明确R WR新版，非2013非WR旧版；原产品页月份未核实。',None,'fuji-web-4.json')

add('小米|儿童手表|米兔儿童手表s1','2024-05','https://news.mydrivers.com/1/982/982548.htm','同期2024-05-28发布报道；候选早一年。原evidence的URL与quote均null，单列无依据，不混入有依据准确率。',False,'mi-web-1.json')
add('小米|家庭屏|xiaomi智能家庭屏11','2025-12','https://www.ithome.com/0/908/020.htm','同期2025-12-25发布，明确11英寸新品；候选2023-04错误，无原依据。',False,'mi-web-4.json')
add('小米|对讲机|小米对讲机3','2022-04','https://www.ithome.com/0/611/344.htm','同期2022-04-05公告小米对讲机3；日期相符，无原URL/quote，单列无依据。',False,'mi-web-1.json')
add('小米|平板|redmipad2','2025-06','https://www.mi.com/uk/product/redmi-pad-2/faq/','官方英国FAQ明确2025年6月推出，先于候选全球2025-08；候选不是首次月份，无原依据。',False,'mi-web-3.json')
add('小米|电视|小米电视4c32英寸','2018-05','https://m.xdjd.cn/Article/525904/7CF87F862DDE/Article.aspx','同期2018-05-25四新品稿精确点名4C 32英寸，日期相符；无原URL/quote，单列无依据。',False,'mi-web-4.json')
add('小米|电视|小米电视4a65英寸','2017-03','https://www.cheaa.org/upload/files/2017/5/1014484415.pdf','家电行业期刊2017年4月号记录3月21日发布会并点名43/49/55/65四尺寸；原global产品页月份未核实。',None,'mi-web-3.json')
add('小米|宠物饮水机|米家智能宠物饮水机2','2024-12','https://www.ithome.com/0/819/782.htm','同期2024-12-24新款上市稿明确二代，型号匹配；候选2023-04错误，原URL无首发月份引文。',False,'mi-web-2.json')
add('小米|REDMI路由器|xiaomi路由器be7200pro','2026-05','https://www.ithome.com/0/947/128.htm','同期2026-05-07发布BE7200 Pro，5月13日首销，非其他BE机型；候选2024-12错误，无原依据。',False,'mi-web-4.json')
add('小米|旧款机型|红米6a','2018-06','https://news.mydrivers.com/1/591/591743.htm','同期官方促销转述稿回溯6月12日发布红米6A，另有同年发布会报道一致；原产品页月份未核实。',None,'mi-web-3.json')
add('小米|手表|米动手表青春版','2017-07','https://www.eepw.com.cn/article/201707/361951.htm','同期2017年7月稿明确7月4日晚发布；原厂手册亦标2017.07.17，4月是米动健康手环，不能混为同一商品。无原依据。',False,'mi-web-4.json')

add('比亚迪|汽车|比亚迪汉2023款dm-i','2023-05','https://auto.sina.com.cn/newcar/2023-05-18/detail-imyuetha5135727.shtml','同期5月18日发布汉DM-i冠军版；3月16日为汉EV冠军版与唐DM-i，不能借给汉DM-i。原URL不可访问。',False,'byd-web-1.json')
add('比亚迪|汽车|比亚迪汉dm-i智驾版','2025-02','https://www.pcauto.com.cn/nation/4694/46942205.html','同期2025-02-10发布稿精确点名汉DM-i智驾版及5配置，不只用全系21款宣传；日期相符，无原依据。',False,'byd-web-1.json')
add('比亚迪|汽车|比亚迪汉2024款ev','2024-02','https://www.yicai.com/brief/102007737.html','同期2月28日比亚迪官博发布转述明确汉EV荣耀版；日期相符，无原依据。',False,'byd-web-2.json')
add('比亚迪|汽车|比亚迪汉2024款dm-p','2024-02','https://www.autohome.com.cn/news/202402/1293796.html?from=m&platform-key=pc','同期2月28日上市稿精确包含2024款汉DM-p战神版；日期相符，原URL本次不可访问，未核实。',None,'byd-web-1.json')
add('比亚迪|汽车|比亚迪汉2024款dm-i','2024-02','https://www.yicai.com/brief/102007737.html','同期2024-02-28转述官博明确汉DM-i荣耀版；日期相符，无原依据。',False,'byd-web-2.json')
add('比亚迪|汽车|比亚迪汉2023款dm-p','2023-05','https://auto.sina.com.cn/newcar/2023-05-18/detail-imyuetha5135727.shtml','同期2023-05-18正式发布汉DM-p战神版，非3月汉EV冠军版；无原依据，单列错误。',False,'byd-web-1.json')
add('比亚迪|汽车|比亚迪汉2022款dm-i','2022-04','https://www.autohome.com.cn/news/202204/1242832.html?from=m&platform-key=pc','同期2022-04-10新汉家族发布稿明确DM-i/DM-p，日期相符；模型自称链接为示意，不是确知原链接，原依据不合格。',False,'byd-web-1.json')
add('比亚迪|汽车|比亚迪汉2023款ev','2023-03','https://www.nbd.com.cn/articles/2023-03-16/2714042.html','同期2023-03-16记者从官方获悉当晚发布汉EV冠军版，日期相符；无原依据。',False,'byd-web-2.json')
add('比亚迪|汽车|比亚迪夏2026款dm-i','2025-11','https://www.byd.com/cn/live-list/livedetail138','LLM弃答，按要求不算错或对。官方直播目录明确2026款夏于2025-11-04上市发布，正确值独立记录。',None,'byd-web-3.json')
add('比亚迪|汽车|比亚迪宋prodm-i飞驰版','2026-04','https://m.ithome.com/html/941912.htm','LLM弃答，按要求不算错或对。同期2026-04-22稿转述比亚迪官方宣布该精确版本上市；不是普通2026款宋Pro。',None,'byd-web-3.json')

def build():
    queue=json.loads((P/'review-queue.json').read_text());reviews=[]
    for brand,items in queue.items():
        for o in items:
            v=V.get(o['family'])
            if not v and o.get('proposal',{}).get('date') is None:
                v=dict(correct_date=None,verification_url=None,verification_note='模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。',original_evidence_supported=None,evidence_artifact=None)
            if not v:continue
            date=o.get('proposal',{}).get('date')
            reviews.append(dict(checked_at=datetime.now(timezone.utc).isoformat(),family=o['family'],brand=brand,model=o['model'],llm_date=date,has_evidence=o.get('has_evidence',False),original_evidence=o.get('proposal',{}).get('evidence'),correct=(date==v['correct_date']) if date and v['correct_date'] else None,**v))
    (P/'reviews.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':build()
