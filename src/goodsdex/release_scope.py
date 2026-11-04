"""Release denominator policy. Classification never deletes or rewrites goods."""
import re
from collections import Counter
from .accessories import classify

POLICY = 'machine-release-v1'
THIRD = re.compile(r'生活优选|^(?:8H|90分|Free Tie|TS|AMAZFIT|Amazfit|米动|1MORE|Yeelight|ZMI|70迈|九号|小蚁|小默|华来|大方|贝医生|飞利浦|青米|最生活|日常元素|小卫质品|Populele|AirPOP|电助力折叠自行车)', re.I)
# Peripheral nouns precede model-name matches. A bundle's principal device wins.
PART = re.compile(r'相纸|标签纸|上下水装置|自拍杆|充电套装|充电站|服务|维修|会员|日租卡|权益|定金|礼盒|(?:主刷|边刷|刷罩|主刷罩|地刷|拖地附件|抽水软管|净水盒|相纸|标签纸|墨水|存储卡|配重块|传感器)$|遥控器|手机夹|触控笔|笔尖|专用抗光屏|全能手柄|滤镜|ND\s*镜|镜头$')
LIFESTYLE = re.compile(r'包|旅行箱|登机箱|枕|床垫|沙发|毛巾|浴巾|T恤|衬衫|西装|西裤|板鞋|运动鞋|眼镜架|太阳镜|偏光|防蓝光|护目镜|口罩|伞|吊坠|签字笔|中性笔|手动|牙线|洗手液|保温杯|水杯|玻璃杯|保温壶|吸管杯|直饮杯|运动杯|腰靠|手链|汤锅|胶囊咖啡(?!机)|工具箱|螺丝刀套装|积木|插线板|插排|转换器|无线充|车充')
DEVICE = re.compile(r'红米|小米\s*(?:\d|MIX|Max|Note|VR)|Redmi|Xiaomi|两季扇|小饭煲|滚筒|墙壁插座|轨道插座|喷墨打印|户外多功能灯|车载逆变器|游戏本|对讲机|电饭|词典笔|露营灯|冲牙器|轨道灯|熨烫机|足浴|阅读灯|热水瓶|管线机|电蒸锅|学习灯|修剪器|电热毯|养生壶|咖啡机|空气炸锅|电煮锅|取暖器|烘干机|暖菜板|电火锅|电陶炉|直发梳|智能音频眼镜|AI眼镜|净饮机|吊灯|中控屏|茶吧机|制冰机|电烤箱|三洗|血压计|故事机|随身灯|放大器|滑板车|无人机|报警器|石英表|智能闹钟|手机|笔记本|平板|相机|摄像|电视|冰箱|空调|洗衣机|洗烘|音箱|耳机|手环|手表|电话|打印机|路由|电力猫|盒子|家庭影院|网关|记录仪|后视镜|机器人|吸尘器|洗地机|净水|饮水机|过滤器|热水器|洗碗机|电饭煲|电压力锅|电磁炉|水壶|电热杯|电暖|暖风|风扇|落地扇|塔扇|循环扇|加湿|除湿|净化|除螨|吹风|电动剃须|电动牙刷|理发|微波炉|蒸烤|微烤|料理机|破壁|豆浆|榨汁|门锁|门铃|猫眼|显示器|智能家庭屏|智能家庭面板|控风面板|空气管理面板|麦克风|投影|激光影院|投屏|净烟机|油烟机|燃气灶|烟灶|台灯|床头灯|吸顶灯|灯泡|夜灯|筒灯|射灯|面板灯|灯带|洗手机|喂食器|秤|检测仪|温湿度|检测笔|螺丝刀|电钻|驱蚊器|手电筒|充电宝|移动电源|断电保护电源|交换机|传感器|鼠标|智能插座|口袋吉他|智能哑铃', re.I)


def release_scope(row):
    name = str(row.get('name') or '')
    if THIRD.search(name):
        return dict(tier='third_party_selection', reason='第三方品牌/生活优选；商城归属不代表制造品牌')
    if row.get('brand') in ('Apple', '惠普', '比亚迪', '小米汽车'):
        return dict(tier='machine', reason='独立整机目录及精确型号')
    if row.get('brand') == '富士':
        return dict(tier='accessory' if row.get('camera_role') == 'lens' or row.get('category') == '相机镜头' else 'machine', reason='镜头单列配件；机身及套机为整机')
    if row.get('brand') == '大疆':
        return dict(tier='accessory' if row.get('kind') == 'accessory' else 'machine', reason='独立整机/含整机套装；不将套装日期等同基础机型')
    decision = classify(row)
    if re.search(r'小米车载公网对讲机|13.3\" i5', name):
        return dict(tier='machine', reason='人工核对：整机与附送支架/省略笔记本名')
    if decision['accessory'] or row.get('kind') == 'service' or PART.search(name):
        return dict(tier='accessory', reason='配件/耗材/服务不适用整机上市日期')
    # Lifestyle peripherals may have a model number but are outside device scope.
    if LIFESTYLE.search(name) and not re.search(r'智能音频眼镜|电动|洗衣机|机器人|打印机|充电宝|电热杯', name):
        return dict(tier='accessory', reason='生活周边/无独立整机上市概念')
    if row.get('kind') == 'machine' or DEVICE.search(name):
        return dict(tier='machine', reason='独立设备型号/功能；保留旧款和无日期整机')
    return dict(tier='accessory', reason='非整机周边；逐行分类清单可复核')


def displayable(release):
    return bool(release and release.get('date') and release.get('usage') != 'disabled'
                and release.get('display_allowed') is not False
                and release.get('internal_only') is not True
                and release.get('source') != 'llm')


def scope_coverage(rows):
    brands = {}
    tiers = Counter()
    for row in rows:
        tier = release_scope(row)['tier']
        tiers[tier] += 1
        b = brands.setdefault(row.get('brand') or '其他', dict(total=0, machine=0, accessory=0,
            third_party_selection=0, product_covered=0, series_only_covered=0, covered=0, missing=0))
        b['total'] += 1
        b[tier] += 1
        if tier == 'machine':
            if displayable(row.get('release')):
                b['product_covered'] += 1
            elif displayable(row.get('release_series')):
                b['series_only_covered'] += 1
            else:
                b['missing'] += 1
    for b in brands.values():
        b['covered'] = b['product_covered'] + b['series_only_covered']
        b['coverage'] = b['covered'] / b['machine'] if b['machine'] else None
        b['product_coverage'] = b['product_covered'] / b['machine'] if b['machine'] else None
    return dict(policy=POLICY, label='整机口径覆盖率', denominator='machine',
        counting_unit='published_rows', total=len(rows), tiers=dict(tiers), brands=brands,
        note='对外只报整机口径覆盖率；同时披露配件周边和第三方精选条数。单品与系列分列，LLM和页面首存不计入。')
