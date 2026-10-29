"""Versioned, deterministic index/detail publication. goods.json stays byte-identical."""
import base64
import gzip
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

SCHEMA = 1
SHARDS = 64
INDEX_FIELDS = 'id name category categories price price_kind image brand product_id record_level product_type series trim model_year kind gid model image_url lookup_keys discontinued camera_role body_id lens_id aliases variant_hint bundle source_url'.split()
BRANDS = {'小米': 'mi_cn', 'Apple': 'apple_cn', '大疆': 'dji', '富士': 'fuji', '比亚迪': 'byd', '小米汽车': 'xiaomi_ev'}
# Same literal fields consumed by the API list-facts projection; never copy raw sections.
FACT_KEYS = '容量 净水容量 污水容量 尘盒容量 尘袋容量 屏幕尺寸 尺寸 加热方式 适用人数 内胆材质 吸力 水箱容量 功率 能效等级 连接方式 颜色 洗涤容量 烘干容量 总容量 最大吸力 额定功率 整机功率 存储容量 运行内存 内存容量 固态硬盘 电池容量 额定容量 屏幕分辨率 分辨率 最高刷新率 匹数 能效 制冷方式 门体类型 适用面积 无线协议 无线速率 材质 腕带材质 表带材质 防水等级 防水级别 续航时间 续航时长 充电方式 刀头数量 刀头材质 刷毛 清洁模式 主过滤技术 滤芯数量 常温水流速 套数 安装方式 锁芯 开锁方式 门锁颜色 CPU型号 CPU类型 处理器 屏幕类型 面板类型 蓝牙版本 镜头清晰度 输出参数 产品尺寸 外形尺寸 麦克风 扬声器 出音方式 变频/定频 定频/变频 操控方式 摇头角度 打印技术 打印分辨率 面板材质 风量风速 火力/气源 最大静压 烟机能效 灶具能效 烟机尺寸 最大风速 马达转速 滤网类型 有线快充 无线快充 网络类型 screen.size ram rom cpu battery power.rated wind.speed motor.rpm battery.total battery.single water.ip anc.depth driver'.split() + ['Wi-Fi 频段']


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def shard_for(key):
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % SHARDS


def build_shards(public):
    public = Path(public)
    rows = json.loads((public / 'goods.json').read_bytes())
    indexes = {slug: [] for slug in [*BRANDS.values(), 'other']}
    details = [dict() for _ in range(SHARDS)]
    for ordinal, row in enumerate(rows):
        key = row['id']
        if not isinstance(key, str) or not key:
            raise ValueError('missing string id')
        p = row.get('params') or {}
        item = {k: row[k] for k in INDEX_FIELDS if k in row}
        # Exact legacy search includes JSON.stringify(params), including repeated sections.
        # Store this text compressed; the API inflates text, never parses heavy params.
        text = json.dumps(p, ensure_ascii=False, separators=(',', ':'))
        values = {k: p[k] for k in [*FACT_KEYS, 'variant_attrs', 'model_year', 'model'] if k in p}
        sections = [s for s in p.get('specs_sections', []) if re.sub(r'\d+$', '', str(s.get('heading'))) in ['存储', '存储设备', '容量', '内存', '外观', '颜色', '无线连接']]
        if sections:
            values['specs_sections'] = sections
        item['_query'] = dict(ordinal=ordinal, values=values,
            attributes={k: v.strip() for k, v in p.items() if re.search('[\u3400-\u9fff]', k) and isinstance(v, str) and v.strip()},
            search_text=text.lower())
        indexes[BRANDS.get(row.get('brand'), 'other')].append(item)
        bucket = details[shard_for(key)]
        if key in bucket:
            bucket[key].setdefault('_catalog_conflicts', []).append(row)
        else:
            bucket[key] = dict(row)
    files = {}
    def write(name, value, count):
        raw = encode(value)
        target = public / name
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix('.tmp')
        tmp.write_bytes(raw)
        tmp.replace(target)
        files[name] = dict(sha256=hashlib.sha256(raw).hexdigest(), count=count, bytes=len(raw))
    for slug, items in indexes.items():
        queries = [item.pop('_query') for item in items]
        packed = base64.b64encode(gzip.compress(encode(queries), mtime=0)).decode()
        write(f'index/{slug}.json', dict(items=items, query_gzip=packed), len(items))
    for n, bucket in enumerate(details):
        write(f'detail/{n:02x}.json', bucket, len(bucket))
    raw = (public / 'goods.json').read_bytes()
    files['goods.json'] = dict(sha256=hashlib.sha256(raw).hexdigest(), count=len(rows), bytes=len(raw), usage='full export; do not use for clients')
    meta_path = public / 'meta.json'
    meta = json.loads(meta_path.read_bytes()) if meta_path.exists() else {}
    meta.update(schema=SCHEMA, count=len(rows), files=files,
                detail_sharding=dict(algorithm='sha256-first32-mod', count=SHARDS),
                index_order='ascending _query.ordinal', unique_count=sum(len(b) for b in details))
    # Generation time is managed by the upstream finalizer.
    from datetime import datetime, timezone
    meta.setdefault('generated_at', datetime.now(timezone.utc).isoformat())
    tmp = meta_path.with_suffix('.tmp')
    tmp.write_bytes(encode(meta))
    tmp.replace(meta_path)
    return meta
