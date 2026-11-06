"""Append reviewed durable devices; existing catalog rows are immutable here."""
from copy import deepcopy
import json
import re
import unicodedata
from pathlib import Path
from .mijia_baike import norm
from .price_semantics import comparable

B = set('开关 无线开关 控制面板 网关 灯泡 灯带 筒射灯 面板灯 轨道灯 窗帘电机 红外遥控 红外遥控器 Wi-Fi信号放大器 温控器 汽车氛围灯'.split())
C = set('插座／插排 空调插座 路由器 吸顶灯 台灯 其他灯 吊灯 风扇灯 立式学习灯 夜灯 显示器挂灯 床头灯 落地灯 充电桩 家居工具 计时器 手写板 智能枕头'.split())
A = set('电热毯 门锁 摄像机 冰箱 猫眼门铃 按摩器/椅 养生壶 饮水机 电饭煲 笔记本 净水机 储能电源 风扇 扫地机器人 空调 电视\u0020/\u0020盒子 洗衣/烘干机 洗碗机 晾衣架 咖啡机 抽油烟机 体重／体脂秤 电暖器 浴霸 空气净化器 热水器 蒸烤箱 电热水壶 空气炸锅 智能鱼缸 宠物饮水机 加湿器 投影仪 茶吧机 打印机 冲牙器 手表 智能存储 压力锅 足浴器 吸尘器 牙刷 显示器 宠物喂食器 擦地机 除湿机 音箱 哑铃 消毒柜 对讲机 手环 跳绳 香薰机 微波炉 健腹轮 保险箱 散热器 榨汁机 麦克风 雕刻机 行车记录仪 电蒸锅 集成灶 电磁炉 健身车 跑步机 血压计 猫砂盆 走步机 滑板车 驱蚊器 体温计 新风机 空气检测仪 时钟 故事机 智能后视镜 收音机 智能门 凉霸 智能镜 马桶（盖） 多功能料理锅'.split()) | {'电视 / 盒子'}

def norm(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC',s or '').casefold())

def classify(d):
    cat, name = d['categoryName'], d['name']
    if cat in B or '传感器' in cat or re.search(r'滤芯|滤网|耗材|替换装|电源线|连接线|灯泡|开关面板|开关模块|智能开关|空调伴侣|空气管理面板(?![）)])|^热水器遥控$|空调控制器|散热背夹|演示|测试',name):
        return 'B', '配件/基础设施，用户明确排除'
    if cat in C:
        return 'C', '插座/路由器/灯具整机或用途边界，待用户决定'
    if cat in A:
        return 'A', '独立耐用整机'
    return 'C', '未在整机白名单，需人工决定'

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/mihome-intake.json'

def apply_intake(rows, manifest=None):
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text()) if DEFAULT.exists() else {'schema':1,'items':[]}
    if manifest.get('schema') != 1:
        raise ValueError('Unsupported Mi Home intake')
    result = deepcopy(rows)
    ids = {r['id'] for r in result}
    names = {norm(r.get('name') or '') for r in result}
    models = {r.get('miio_model') or r.get('mihome_model') for r in result}
    seen = set()
    for e in manifest['items']:
        r=e['row'];key=r['id']
        if key in seen or e.get('classification')!='A' or not e.get('directory_sha256') or len(e['directory_sha256'])!=64:
            raise ValueError('Unreviewed/duplicate Mi Home intake')
        seen.add(key)
        if classify(dict(categoryName=r.get('category_mihome'),name=r.get('name_mihome','')))[0] != 'A':
            raise ValueError('Accessory/infrastructure/undecided intake forbidden')
        if not r.get('miio_model') or not isinstance(r.get('mihome_pd_id'),int) or r.get('image_scope')=='device_icon':
            raise ValueError('Invalid device identity/image role')
        if r.get('source')=='mihome' and (key != f"mihome:{r['mihome_pd_id']}" or r.get('image') or r.get('price') is not None):
            raise ValueError('Device archive cannot supply channel price/image')
        if r.get('price') is None and (r.get('price_missing')!='no_channel_price' or comparable(r)):
            raise ValueError('Unpriced device entered price comparison')
        if r.get('source')!='mihome' and not e.get('channel_verified'):
            raise ValueError('Channel identity unverified')
        if r.get('release') or r.get('release_date'):
            raise ValueError('Directory intake supplies no launch dates')
        if key in ids or r['miio_model'] in models or norm(r['name']) in names:
            continue
        result.append(deepcopy(r));ids.add(key);models.add(r['miio_model']);names.add(norm(r['name']))
    return result
