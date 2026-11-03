"""Explicit source and identity review. No search/fuzzy/date generation at replay."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.release_dates import digest
from goodsdex.series_release import identity, validate_batch

def read(path):
    return json.loads(Path(path).read_text())

def write(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def web(url, needle, publisher, published_at, length=220):
    p = OUT / 'evidence' / (hashlib.sha256(url.encode()).hexdigest()[:16] + '.json')
    c = read(p)
    assert not c.get('error') and not c.get('body_unavailable'), url
    normalized = re.sub(r'\s+', '', c['text'])
    i = normalized.index(re.sub(r'\s+', '', needle))
    e = {k: c[k] for k in ('url', 'capture_url', 'capture_file', 'sha256', 'captured_at')}
    e.update(quote=normalized[i:i+length], locator='归档 HTML 正文；移除排版空白后以 needle 精确定位',
             publisher=publisher, published_at=published_at, source_type='third_party', verified=True)
    assert hashlib.sha256((ROOT / e['capture_file']).read_bytes()).hexdigest() == e['sha256']
    return e

def official(stem, needle, length=170):
    p = ROOT / stem
    c = read(p.with_suffix('.json'))
    text = re.sub(r'\s+', '', p.with_suffix('.txt').read_text())
    i = text.index(needle)
    # The web PDF capture for 25Q3 stores PDF bytes with a .bin suffix.
    matches = [q for q in p.parent.glob(p.name + '.*')
               if q.suffix != '.json' and hashlib.sha256(q.read_bytes()).hexdigest() == c['sha256']]
    if not matches:
        matches = [q for q in (ROOT / 'data/release-dates/round2/raw').glob('mi*')
                   if q.is_file() and q.suffix not in ('.txt', '.json')
                   and hashlib.sha256(q.read_bytes()).hexdigest() == c['sha256']]
    assert matches, stem
    return dict(url=c['url'], sha256=c['sha256'], captured_at=c['captured_at'],
                capture_file=str(matches[0].relative_to(ROOT)), quote=text[i:i+length],
                hash_scope=c.get('hash_scope', 'response_bytes'),
                locator='官方业绩公告；归档抽取文本仅移除排版空白',
                source_type='official', publisher='xiaomi', verified=True)

def build():
    rows = json.loads(gzip.decompress((OUT / 'baseline.json.gz').read_bytes()))
    byid = {r['id'].split(':')[-1]: r for r in rows if r.get('brand') == '小米'}
    batches = []

    def add(key, family, generation, ids, date, evidence, second=None, second_date=None, reason='', event='announcement'):
        bid = 'mi-expansion-20261104-' + key
        source = evidence['source_type']
        release = dict(date=date, granularity={4:'year',7:'month',10:'day'}[len(date)],
                       source=source, market='CN', event=event, level='series', evidence=evidence)
        if second:
            release['crosschecks'] = [dict(source=second['source_type'], date=second_date or date,
                batch_id=bid, market='CN', event=event, independent=True,
                independence_reason=f"原始供稿机构 {evidence['publisher']} 与 {second['publisher']} 不同；核对署名/来源，无相互转载标记。",
                evidence=second)]
        batch = dict(id=bid, series=family, generation=generation, series_release=release,
            members=[dict(id=byid[i]['id'], reviewed_name=byid[i]['name'],
                          identity_sha256=digest(identity(byid[i])), identity_reason=reason) for i in ids])
        for member in batch['members']:
            alternatives = sorted({digest(identity(r)) for r in rows if r['id']==member['id']}
                                  - {member['identity_sha256']})
            if alternatives:
                assert key == 'k90', 'New duplicate identities require explicit review'
                member['identity_sha256_alternates'] = alternatives
                member['identity_reason'] += ' 当前同ID有英文字段/中文字段两份参数投影；逐值复核一致，分别冻结两个精确哈希，不做运行时字段归一或跳过漂移。'
        validate_batch(batch)
        batches.append(batch)

    add('max2', '小米 Max 2', '2017 首发 4+64/128GB；不含后加32GB', ['10000057','5780','5781'], '2017-05-25',
        web('https://www.ithome.com/0/310/477.htm','[15:39:01]','ithome','2017-05-25'),
        web('https://news.mydrivers.com/blog/20170525.htm','今天下午的新品发布会，小米发布了第二代大屏续航手机小米Max 2','mydrivers','2017-05-25'),
        reason='发布会实录和独立报道都明确4+64、4+128；只纳入同名基础页与这两种容量。')
    add('6x', '小米 6X', '2018-04 首发三规格；不含4+32GB', ['10000091','7895','7897'], '2018-04-25',
        web('https://mobile.zol.com.cn/686/6865715_all.html','北京时间4月25日下午','zol','2018-04-25'),
        web('https://www.cww.net.cn/article?id=430951','（CWW）4月25日','cww','2018-04-25'),
        reason='两篇独立首发报道明确6X及首发6+64/6+128；4+32后来发布，明确排除8154。')
    add('note5', '红米 Note 5', '2018 中国大陆首发；不含印度Note5/后加128GB', ['10000084','7763','7765'], '2018-03-16',
        web('https://mobile.zol.com.cn/681/6816826_all.html','2018年3月16日下午','zol','2018-03-16'),
        web('https://www.ithome.com/0/352/708.htm','3月16日， 小米在北京发布了红米Note 5','ithome','2018-03-26'),
        reason='中国大陆骁龙636批次，首发报道逐项列3+32、4+64、6+64，与两条SKU相符。')
    add('pad4', '小米平板 4', '2018-06-24 8英寸 WiFi32/64GB、LTE64GB公开发布', ['10000108','8385','8387','8388'], '2018-06-24',
        web('https://www.ithome.com/0/366/649.htm','IT之家 6月24日消息','ithome','2018-06-24'),
        web('https://mobile.zol.com.cn/692/6920475_all.html','昨晚，小米官方突然发布了红米6 Pro和','zol','2018-06-25'),
        reason='6月25日稿件明确“昨晚”，回指24日；正文列全三个首发规格，不借用后来平板4 Plus。')
    add('redmi6', '红米 6', '2018 Helio P22 中国大陆发布', ['10000103'], '2018-06-12',
        web('https://www.ithome.com/0/365/048.htm','小米在6月12日发布了红米6','ithome','2018-06-15'),
        web('https://tech.sina.com.cn/mobile/n/n/2019-01-03/doc-ihqhqcis2591683.shtml','红米6/红米6A—6月12日','pcpop','2019-01-03'),
        reason='红米6基础型号；P22、初代规格匹配；新浪标注原稿泡泡网，按pcpop记录，不当新浪独立原创。')
    add('redmi6a', '红米 6A', '2018 初版；仅6月13日已归档初版商品页', ['8274'], '2018-06-12',
        web('https://tech.sina.com.cn/mobile/n/n/2019-01-03/doc-ihqhqcis2591683.shtml','红米6/红米6A—6月12日','pcpop','2019-01-03'),
        web('https://news.mydrivers.com/blog/20180612.htm','6月11日， 小米公司发布了两款千元下新机红米6、红米6A','mydrivers','2018-06-12'), second_date='2018-06-11',
        reason='8274来自2018-06-13初版官方归档；独立报道相差1天，按≤14天采信。7月归档且容量未知的10000110不纳入。')
    add('mi8-september', '小米 8 青春版 / 屏幕指纹版', '2018-09-19 成都发布；与5月8/SE/探索版分开', ['10000117','10000118','8803'], '2018-09-19',
        web('http://it.people.com.cn/n1/2018/0920/c1009-30305965.html','人民网成都9月20日电','people','2018-09-20'),
        web('https://www.ithome.com/0/384/099.htm','IT之家 9月19日消息','ithome','2018-09-19'),
        reason='人民网明确19日两款，IT之家当日屏幕指纹版报道明确6/8+128GB；青春版另以385034核对。')
    # Separate evidence for Youth: the fingerprint-only article cannot corroborate it.
    batches[-1]['series_release']['crosschecks'].append(dict(
        source='third_party',date='2018-09-19',batch_id=batches[-1]['id'],market='CN',event='announcement',
        independent=True,independence_reason='人民网原创与IT之家原创分属两个供稿机构；青春版精确型号复核。',
        evidence=web('https://www.ithome.com/0/385/034.htm','小米8青春版手机发布于9月19日','ithome','2018-09-24')))
    fingerprint = batches[-1]
    youth = deepcopy(fingerprint)
    youth['id'] += '-youth'
    youth['series'] = '小米 8 青春版'
    youth['members'] = [m for m in youth['members'] if m['id'].endswith(':10000117')]
    youth['series_release']['crosschecks'] = youth['series_release']['crosschecks'][1:]
    youth['series_release']['crosschecks'][0]['batch_id'] = youth['id']
    fingerprint['series'] = '小米 8 屏幕指纹版'
    fingerprint['members'] = [m for m in fingerprint['members'] if not m['id'].endswith(':10000117')]
    fingerprint['series_release']['crosschecks'] = fingerprint['series_release']['crosschecks'][:1]
    batches.append(youth)
    add('redmi6pro', '红米 6 Pro', '2018-06-24 公开上架（非25日计划发布）', ['10000107'], '2018-06-24',
        web('https://www.ithome.com/0/366/649.htm','IT之家 6月24日消息','ithome','2018-06-24'),
        web('https://mobile.zol.com.cn/692/6920475_all.html','昨晚，小米官方突然发布了红米6 Pro和','zol','2018-06-25'),
        reason='两篇报道共同指向24日晚公开产品/价格；不以原定25日替代实际提前上架。')
    add('max3', '小米 Max 3', '2018-07-19 中国大陆发布', ['10000111'], '2018-07-19',
        web('https://www.ithome.com/0/371/561.htm','IT之家 7月19日消息','ithome','2018-07-19'),
        web('https://tech.ifeng.com/c/7ef0GUKgj4a','7月19日消息','ifeng','2018-07-19'),
        reason='同代骁龙636、6.9英寸、5500mAh；只基础型号，不跨Max2。')
    add('tv4a', '小米电视 4A', '2017-03-21 首发43/49/55/65英寸；不含后来32/40/50/58英寸', ['5353','6632','6633','6634'], '2017-03-21',
        web('https://m.cnr.cn/tech/20170321/t20170321_523669761.html','央广网科技3月21日消息','cnr','2017-03-21'),
        web('https://www.ithome.com/0/306/197.htm','3月21日小米在北京正式发布了小米电视4A','ithome','2017-04-25'),
        reason='两个独立稿明确四个尺寸，按尺寸白名单纳入；体育版/影院版另批，全部排除。')
    add('tv4', '小米电视 4', '2017-05-18 首发49/55/65英寸；不含75英寸、影院版', ['5892','7095'], '2017-05-18',
        web('https://www.ithome.com/0/309/475.htm','IT之家 5月18日消息','ithome','2017-05-18'),
        web('https://news.sciencenet.cn/htmlnews/2017/5/376716.shtm','5月18日下午，小米2017年度旗舰电视发布会','sciencenet','2017-05-18'),
        reason='独立报道同日明确55/65，49无当前行；75/影院版未获同批证据不纳入。')
    add('hoodp1', '米家智能净烟机 P1', '2022-08-11 初版净烟机；不含后续烟灶组合', ['16350'], '2022-08-11',
        web('https://www.ithome.com/0/634/620.htm','IT之家 8 月 11 日消息','ithome','2022-08-11'),
        web('https://news.mydrivers.com/blog/20220811.htm','爆炒不跑烟！米家智能净烟机P1发布','mydrivers','2022-08-11'),
        reason='精确P1整机，两源同日；燃气灶及各年新增组合装没有被首发报道覆盖，不继承。')
    add('ceilingpro', '米家智能吸顶灯 Pro', '2022-10-11 客厅/卧室初版；不含超薄版及2025组合装', ['16606'], '2022-10-11',
        web('https://www.ithome.com/0/646/016.htm','IT之家 10 月 11 日消息','ithome','2022-10-11'),
        web('https://news.mydrivers.com/blog/20221011.htm','599元起米家推出智能吸顶灯Pro','mydrivers','2022-10-11'),
        reason='同名Pro首发报道明确卧室/客厅初版；2026超薄Pro与后组装套餐独立留空。')
    add('ceiling2024', '米家吸顶灯套系', '2024-08-29 D20/D30/D40/L60/L90 首批', ['20350'], '2024-08-29',
        web('https://www.ithome.com/0/791/941.htm','IT之家 8 月 29 日消息','ithome','2024-08-29'),
        web('https://news.mydrivers.com/blog/20240829.htm','快科技8月29日消息，米家吸顶灯套系预售开启','mydrivers','2024-08-29'),
        reason='正文逐个列五个型号，当前套系页匹配；2025/26一室/两室组合没有同日推出证据不继承。')
    add('fridge216', '米家冰箱 216L 三门风冷', '2022-03-16 122+32+62L、0.63度、525×648mm；不含2026款', ['15638'], '2022-03-16',
        web('https://www.ithome.com/0/607/951.htm','IT之家 3 月 16 日消息','ithome','2022-03-16'),
        web('https://news.mydrivers.com/blog/20220316.htm','首发1499元！小米发布米家冰箱无霜三门216L','mydrivers','2022-03-16'),
        reason='容量分区、尺寸、风冷、0.63度/天精确匹配；不纳入同容量直冷/2026新款23579。')
    add('fridge610', '米家冰箱 610L 对开', '2022-05-24 墨羽岩双变频0.99度、227+383L', ['15948'], '2022-05-24',
        web('https://news.mydrivers.com/blog/20220524.htm','2499元！米家610L对开门冰箱发布','mydrivers','2022-05-24'),
        web('https://finance.sina.com.cn/tech/2022-05-24/doc-imizmscu3174190.shtml','DoNews 5月24日消息','donews','2022-05-24'),
        reason='610L分区227/383L、噪音36dB、0.99度均与当前参数相符；新浪为DoNews转载按原供稿机构核对。')
    add('monitor-a27', 'REDMI 显示器 A27', '2026型号、2025-08-01发布、1080P144Hz；不含A27Q/U', ['21636'], '2025-08-01',
        web('https://finance.sina.com.cn/tech/roll/2025-08-01/doc-infimwzc9130991.shtml','快科技8月1日消息','mydrivers','2025-08-01'),
        web('https://article.pchome.net/news/5129.html','8月1日，小米旗下品牌Redmi正式发布A27','pchome','2025-08-01'),
        reason='精确2026款1080P144Hz、DP1.4/HDMI2.0；型号年份不等于发布年份，禁止把2026写成日期。')

    add('k100', 'REDMI K100 Pro / Pro Max', '2026-08-11 双旗舰首发；不含后续K100标准版', ['25135','25140'], '2026-08-11',
        web('https://finance.sina.com.cn/tech/roll/2026-08-11/doc-inimyaac0629173.shtml','C114讯8月11日消息','c114','2026-08-11'),
        web('https://www.ithome.com/0/988/527.htm','IT之家8月11日消息','ithome','2026-08-11'),
        reason='两家原始新闻机构明确Pro与ProMax同日发布；8580/9070mAh、V Series/标准芯片区分与当前SKU相符。')
    add('k90max', 'REDMI K90 Max', '2026-04-21 天玑9500风扇机；不含2025 K90/ProMax', ['23969'], '2026-04-21',
        web('https://finance.eastmoney.com/a/202604213712893426.html','REDMIK90Max4月21日晚正式发布','cnstock','2026-04-21'),
        web('https://www.ithome.com/0/941/920.htm','小米REDMIK90Max手机昨日正式发布','ithome','2026-04-22'),
        reason='上海证券报记者刘暄原稿与IT之家独立稿一致，22日“昨日”指21日；不是K90 ProMax。')
    add('kpad2', 'REDMI K Pad 2', '2026-04-21 8.8英寸天玑9500首发', ['23974'], '2026-04-21',
        web('https://www.ithome.com/0/941/794.htm','IT之家4月21日消息','ithome','2026-04-21'),
        web('https://finance.eastmoney.com/a/202604213712893426.html','此外，同场发布的还有REDMIKPad2','cnstock','2026-04-21'),
        reason='两家稿件明确同场KPad2；8.8英寸165Hz、9100mAh、天玑9500与当前参数一致，不跨KPad初代。')
    add('turbo5', 'REDMI Turbo 5', '2026-01-29 标准版天玑8500-Ultra', ['22526'], '2026-01-29',
        web('https://www.ithome.com/0/917/636.htm','IT之家1月29日消息','ithome','2026-01-29'),
        web('https://finance.sina.com.cn/jjxw/2026-01-29/doc-inhiyrwi0997681.shtml','北京商报讯（记者陶凤王天逸）1月29日','bbt','2026-01-29'),
        reason='北京商报原创原句同时点名Turbo5与Max；标准版7560mAh/6.59英寸匹配，不借用Max参数。')
    add('turbo5max', 'REDMI Turbo 5 Max', '2026-01-29 天玑9500s / 9000mAh', ['22527'], '2026-01-29',
        web('https://www.ithome.com/0/917/689.htm','IT之家1月29日消息','ithome','2026-01-29'),
        web('https://finance.sina.com.cn/jjxw/2026-01-29/doc-inhiyrwi0997681.shtml','北京商报讯（记者陶凤王天逸）1月29日','bbt','2026-01-29'),
        reason='同场Max单独建立批次以保留精确代际名称；不跨Turbo4Pro。')
    add('note15', 'REDMI Note 15 / Pro / Pro+', '2025-08-21 中国大陆三款首发；不含15R、15RPro、2026新春版', ['21648','21659','21665'], '2025-08-21',
        web('https://mobile.zol.com.cn/1034/10343887.html','8月21日19:00，REDMI正式发布新品Note15系列','zol','2025-08-21',length=430),
        web('https://finance.sina.com.cn/tech/roll/2025-08-22/doc-infmwmua5453643.shtml','8月21日晚间，REDMI举办了一场新品发布会','pchome','2025-08-21',length=430),
        reason='两篇原始机构稿明确同日三款及各规格；型号精确白名单，不把后续R/新春配色合入。')
    add('pad2se', 'REDMI Pad 2 SE', '2026-04-21 中国大陆WiFi 6+128GB首销；不含5月4G版', ['24235'], '2026-04-21',
        web('https://www.ithome.com/0/941/483.htm','IT之家4月21日消息','ithome','2026-04-21'),
        web('https://pad.zol.com.cn/1169/11692539.html','2026年4月21日，REDMIPad2SE正式上市销售','zol','2026-04-21'),
        reason='两篇稿均确认当日已经开售及6+128GB；9.7英寸、7600mAh匹配，不把计划开售当已发生。',event='availability')
    add('bookpro2026', 'REDMI Book Pro 14 / 16', '2026-04-21 第三代Ultra首发；不含普通Book2026', ['24035','24037'], '2026-04-21',
        web('https://finance.eastmoney.com/a/202604213712893426.html','此外，同场发布的还有REDMIKPad2','cnstock','2026-04-21'),
        web('https://www.ithome.com/0/941/797.htm','IT之家4月21日消息','ithome','2026-04-21'),
        reason='记者发布会稿确认BookPro2026同场，另一独立稿逐项列14/16首发配置；当前14为Ultra5/UltraX7，16同名2026，不给普通Book16/14或2024机型。')
    add('fridge439ice', '米家冰箱 Pro 439L 法式 自动制冰', '2026-09-16 702×597mm双系统玻璃面板；不含旧439L', ['25059'], '2026-09-16',
        web('https://www.ithome.com/1/002/979.htm','IT之家9月16日消息','ithome','2026-09-16'),
        web('https://article.pchome.net/n3_2098/s1/1.html','米家冰箱Pro439L法式开启预售','pchome','2026-09-16'),
        reason='两家原始媒体对同款自动制冰法式439L发布/预售记录一致；无制冰439L、十字439L不是此批。')

    q1='docs/release-dates-round2-20261103/evidence/mi-25q1-release'
    q3='docs/release-dates-round2-20261103/evidence/mi-ir-03-web'
    q24='docs/xiaomi-series-expansion-20261104/evidence/official-mi-24q3'
    add('ac-human', '米家空调 Pro 人感', '2025-05 挂机上出风1.5匹/新风双出风立式3匹', ['21162','21163'], '2025-05',
        official(q1,'2025年5月，我們發佈了一系列智能大家電產品'),
        reason='官方原句点名两个精确版型和匹数；不用人感日期给健康风、强劲风或2026款。')
    add('pad7', 'Xiaomi Pad 7 系列', '2024-10 中国大陆 Pad7/7Pro；不含7S/Ultra', ['20593','20598'], '2024-10',
        official(q24,'2024年10月，我們推出XiaomiPad7系列'),
        reason='官方明确Pad7系列与月份；只Pad7和7Pro，不跨2025的7S Pro/7Ultra。')
    add('pad8', 'Xiaomi Pad 8 系列', '2025-09 中国大陆 Pad8/8Pro；不含海外2026发布', ['21871','21872'], '2025-09',
        official(q3,'2025年9月，我們正式發佈XiaomiPad8系列'),
        reason='官方当季中国大陆发布；11.2英寸、9200mAh平台匹配，不跨Pad9。')
    add('xiaomi17', 'Xiaomi 17', '2025-09 中国大陆首发；不含17T/Ultra海外批次', ['21931'], '2025-09',
        official(q3,'2025年9月，我們發佈新一代智能旗艦手機Xiaomi17系列'),
        reason='官方明确Xiaomi17系列并点名Pro/ProMax；21931为同代标准版，第五代骁龙8至尊版匹配。')
    add('k90', 'REDMI K90', '2025-10 K90/K90ProMax 首发；不含Max/至尊版/K100', ['22172'], '2025-10',
        official(q3,'2025年10月，我們發佈REDMIK90系列'),
        reason='官方原句明确K90和K90ProMax，当前K90重复ID三行原样保留，计3行但只有1个SKU。')

    write(OUT / 'reviewed-new-batches.json', batches)
    print('reviewed',len(batches),'batches;',sum(len(b['members']) for b in batches),'unique ID memberships')
    return batches

if __name__ == '__main__':
    build()
