"""Fujifilm X catalog: public pages only, resumable, single request at a time.

python3 scripts/fuji_catalog.py collect --out data/fuji
python3 scripts/fuji_catalog.py publish --out data/fuji --data-tree /path/to/data-worktree
Requires Python 3.10+ and curl (honors configured HTTP/SOCKS proxy).
A fresh collection uses a fresh --out; cached responses never count as new requests.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import unicodedata
import fcntl
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://www.fujifilm-x.com/zh-cn/products/cameras/'
LISTING = 'https://www.fujifilm.com.cn/cn/zh-hans/consumer/digitalcameras/X'
MODELS = 'x-h2s x-h2 x-pro3 x-t5 x-s20 x-t50 x-t30-iii x-e5 x-m5 x100vi x-hf1'.split()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n')
    tmp.replace(path)


class Stop(RuntimeError):
    pass


class Fetcher:
    def __init__(self, out):
        self.out = Path(out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.log = self.out / 'requests.json'
        self.events = json.loads(self.log.read_text()) if self.log.exists() else []

    def get(self, url):
        if (self.out / 'STOP.json').exists():
            raise Stop('Previous stop recorded; inspect STOP.json. No automatic retry.')
        key = hashlib.sha256(url.encode()).hexdigest()
        dest = self.out / 'cache' / key
        if dest.exists():
            return dest.read_bytes()
        for _ in range(5):
            if len(self.events) >= 300:
                raise Stop('300 request budget exhausted')
            host = urllib.parse.urlsplit(url).netloc
            last = max((e['at'] for e in self.events if e['host'] == host), default=0)
            time.sleep(max(0, 2.15 - (time.time() - last)))
            event = {'url': url, 'host': host, 'at': time.time()}
            self.events.append(event)
            dump(self.log, self.events)  # count requests even if interrupted
            try:
                headers_path = self.out / 'response.headers'
                body_path = self.out / 'response.body'
                result = subprocess.run(['curl', '--silent', '--show-error', '--max-time', '50',
                    '--user-agent', 'goodsdex-catalog/1.0 (public product archive)',
                    '--dump-header', str(headers_path), '--output', str(body_path),
                    '--write-out', '%{http_code}', url], capture_output=True, text=True)
                if result.returncode:
                    raise Stop(result.stderr.strip())
                body = body_path.read_bytes()
                headers = headers_path.read_text()
                location_match = re.search(r'^location:\s*(.+)', headers, re.I | re.M)
                content_match = re.search(r'^content-type:\s*(.+)', headers, re.I | re.M)
                event.update(status=int(result.stdout), bytes=len(body),
                    location=location_match[1].strip() if location_match else None,
                    content_type=content_match[1].strip() if content_match else '')
            except Exception as exc:
                event.update(error=str(exc))
                dump(self.log, self.events)
                dump(self.out / 'STOP.json', event)
                raise Stop(str(exc)) from exc
            dump(self.log, self.events)
            challenge = any(token in body.lower() for token in [b'<title>just a moment', b'cf-chl-', b'/cdn-cgi/challenge-platform'])
            location = event.get('location', '') or ''
            if event['status'] in (403, 429, 412) or challenge or 'risk_handler' in location or 'login.' in location:
                dump(self.out / 'STOP.json', event)
                raise Stop(f"Blocked: {event}")
            if event['status'] in (301, 302, 307, 308):
                url = urllib.parse.urljoin(url, location)
                continue
            if event['status'] != 200:
                raise Stop(f"HTTP failure: {event}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)
            return body
        raise Stop('Too many redirects')


class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []
    def walk(self, tag=None):
        for child in self.children:
            if isinstance(child, Node):
                if tag is None or child.tag == tag:
                    yield child
                yield from child.walk(tag)
    def text(self):
        return ' '.join(' '.join(c.text() if isinstance(c, Node) else c for c in self.children).split())
    def has_class(self, name):
        return name in self.attrs.get('class', '').split()


class DOM(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.current = self.root
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in self.VOID:
            self.current = node
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        node = self.current
        while node.parent is not None:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent
    def handle_data(self, data):
        self.current.children.append(data)


# Every incoming top-level label is explicitly mapped; unknown labels fail closed.
EN = ['Model Name','Lens Mount','Image Sensor','Number Of Effective Pixels','Sensor Cleaning System','Image Processing Engine','Storage Media','File Format Of Still Image','Number Of Recorded Pixels','Panorama','Digital Tele-Converter','Sensitivity','Exposure Control','Exposure Mode','Exposure Compensation','Image Stabilizer','Shutter Type','Shutter Speed','Drive Mode','Focus','Flash','Hot Shoe','Viewfinder','LCD Monitor','Touch Screen Mode','Movie Recording','Film Simulation Mode','Monochromatic Color','Grain Effect','Color Chrome Effect','Color Chrome Blue','Smooth Skin Effect','Dynamic Range Setting','White Balance','Clarity Setting','Self-timer','Interval Timer Shooting','Wireless Transmitter','Bluetooth®','Terminal','Power Supply','Dimensions','Weight','Operation Environment','Starting up period','Accessories Included']
ZH = ['型号','镜头卡口','图像传感器','有效像素数','传感器清洁系统','图像处理引擎','存储介质','静止图像文件格式','记录像素数','全景','数码变焦转换','感光度','曝光控制','曝光模式','曝光补偿','图像防抖','快门类型','快门速度','驱动模式','对焦','闪光灯','热靴','取景器','液晶显示屏','触屏操作','视频拍摄','胶片模拟模式','单色','颗粒效果','彩色正片效果','彩色正片蓝色','肤色效果','动态范围设置','白平衡','清晰度设置','自拍定时器','间隔定时拍摄','无线传输器','蓝牙','端口','电池','外形尺寸','重量','工作环境','启动时间','包含的配件']
LABELS = dict(zip(EN, ZH)) | {z:z for z in ZH} | {
    '机型':'型号', '机型名称':'型号', '录制像素数':'记录像素数',
    '静态图像文件格式':'静止图像文件格式', '自动包围式曝光':'自动包围曝光',
    '闪光灯模式':'闪光灯', 'LCD 液晶显示屏':'液晶显示屏', '子屏':'子屏',
    '视频录制':'视频拍摄', 'HDR模式':'HDR模式', '色彩效果':'彩色正片效果',
    '蓝色彩色正片':'彩色正片蓝色', '创意滤镜':'创意滤镜', '无线 传输':'无线传输器',
    'Microphone Direction Setting':'麦克风指向设置', 'Vlog Mode':'视频日志模式',
    'AUTO Mode Setting':'自动模式设置', 'Portrait Enhancer Lv':'人像增强级别',
    'Lens':'镜头', 'Aperture':'光圈', 'Minimum focus distance (measured from the front of the lens)':'最近对焦距离（从镜头前端测量）',
    '图像格式':'静止图像文件格式', '焦距':'焦距', '转换镜头':'转换镜头', '数码增距转换':'数码变焦转换',
    '取景器（混合式取景器）':'取景器', '触屏模式':'触屏操作', '色彩效果蓝色':'彩色正片蓝色',
    '柔肤效果':'肤色效果', '自拍':'自拍定时器', '无线传输':'无线传输器', '内含配件':'包含的配件',
    'LCD肩屏':'肩屏', 'Continuous shooting':'连拍', '外型尺寸':'外形尺寸', '蓝牙®':'蓝牙', '连拍':'连拍',
}

LABELS.update({v:v for v in list(LABELS.values())})


def raw_specs(source):
    root = DOM(source).root
    pairs = []
    tables = [t for t in root.walk('table') if 'tablepress' in t.attrs.get('id', '')]
    if tables and not any(n.has_class('camera-specifications__block') for n in root.walk()):
        for row in tables[0].walk('tr'):
            parent = row.parent
            while parent and parent.tag != 'table':
                parent = parent.parent
            if parent is not tables[0]:
                continue
            cells = [n for n in row.children if isinstance(n, Node) and n.tag in ('td','th')]
            if not cells:
                continue
            # column-1 is sometimes omitted on rowspan continuation rows.
            first = next((c for c in cells if 'column-1' in c.attrs.get('class','')), None)
            key = first.text() if first else ''
            if key:
                value = ' | '.join(c.text() for c in cells if c is not first)
                pairs.append([key, value])
            elif pairs:
                pairs[-1][1] += ' | ' + ' | '.join(c.text() for c in cells if c is not first)
        return 'table', pairs
    for block in root.walk():
        if not block.has_class('camera-specifications__block'):
            continue
        ancestor = block.parent
        while ancestor and not ancestor.has_class('camera-specifications__block'):
            ancestor = ancestor.parent
        if ancestor:
            continue
        children = [n for n in block.children if isinstance(n, Node)]
        if len(children) < 2:
            raise ValueError('Specification block has no value')
        heading = children[0] if children[0].tag == 'h6' else next(children[0].walk('h6'), None)
        if not heading:
            raise ValueError('Specification block has no h6')
        pairs.append([heading.text(), ' | '.join(c.text() for c in children[1:])])
    return 'div', pairs


def specifications(source):
    structure, pairs = raw_specs(source)
    params = {}
    for label, value in pairs:
        key = LABELS.get(label) or next((v for k,v in LABELS.items() if k.casefold() == label.casefold()), None)
        if not key:
            raise ValueError(f'Unmapped specification label: {label!r}')
        if not value:
            raise ValueError(f'Empty specification: {label}')
        if key in params:
            if key != '取景器':
                raise ValueError(f'Duplicate specification: {label}')
            params[key] += ' | ' + label + ': ' + value
        else:
            params[key] = value
    if not 37 <= len(params) <= 48:
        raise ValueError(f'Unexpected specification count: {len(params)}')
    return structure, params


def identity(slug, lens_slug=None):
    # Accept only exact URL slugs, preserve Roman numerals / S suffixes.
    if not re.fullmatch(r'x[a-z0-9]*(?:-[a-z0-9]+)*', slug):
        raise ValueError(f'Invalid official model slug: {slug}')
    result = 'CN:fuji:model:' + slug
    if lens_slug:
        if not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*', lens_slug):
            raise ValueError('Invalid lens slug')
        result += '-kit-' + lens_slug
    return result


def current_models(source):
    # Navigation links end at product or specifications; exclude GFX explicitly.
    return sorted(set(re.findall(r'/zh-cn/products/cameras/(x[a-z0-9-]+)/(?:specifications/)?[\"\'?#]', source)))


def product(source):
    root = DOM(source).root
    for script in root.walk('script'):
        if script.attrs.get('type') != 'application/ld+json':
            continue
        obj = json.loads(''.join(c for c in script.children if isinstance(c,str)))
        candidates = obj if isinstance(obj,list) else obj.get('@graph', [obj])
        for value in candidates:
            if value.get('@type') == 'Product':
                image = value.get('image')
                if isinstance(image, dict): image = image.get('url')
                if isinstance(image, list): image = image[0]
                return value['name'], html.unescape(image)
    raise ValueError('No Product JSON-LD with main image')


def collect(out):
    out = Path(out)
    f = Fetcher(out)
    listing = f.get(LISTING).decode()
    spec_probe = f.get(BASE + 'x-e5/specifications/').decode()
    observed = current_models(spec_probe)
    dump(out / 'enumeration.json', {'listing_url':LISTING, 'current':observed,
         'listing_models': [n.text() for n in DOM(listing).root.walk('headline') if n.attrs.get(':lv') == '4' and n.text().startswith('FUJIFILM X')]})
    if set(observed) != set(MODELS):
        raise Stop(f'Current model navigation changed: {observed}')
    items = []
    for slug in MODELS:
        spec_html = f.get(BASE+slug+'/specifications/').decode()
        structure, params = specifications(spec_html)
        source_url = BASE + slug + '/'
        product_html = f.get(source_url).decode()
        if re.search(r'class=[\"\'][^\"\']*status-discontinued', product_html):
            raise Stop(f'Current model marked discontinued: {slug}')
        name, image_url = product(product_html)
        image = f.get(image_url)
        is_webp = image.startswith(b'RIFF') and image[8:12] == b'WEBP'
        if not (image.startswith(b'\xff\xd8\xff') or image.startswith(b'\x89PNG') or is_webp):
            raise Stop(f'Not a JPEG/PNG/WebP: {image_url}')
        suffix = '.webp' if is_webp else ('.jpg' if image.startswith(b'\xff') else '.png')
        image_path = Path('data/fuji/images') / (slug + suffix)
        local = out / 'images' / (slug + suffix)
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(image)
        items.append({'id':identity(slug), 'name':'FUJIFILM '+name.removeprefix('FUJIFILM ').strip(),
            'model':params['型号'], 'brand':'富士','kind':'machine','category':'相机',
            'price':None, 'price_kind':'none','price_note':'官网不公开人民币价',
            'price_status':'暂无官方人民币价', 'price_source':None,
            'market':'CN','currency':'CNY','source':'fuji', 'source_url':source_url,
            'spec_url':BASE+slug+'/specifications/', 'image':image_path.as_posix(),
            'image_local_path':image_path.as_posix(), 'image_original_url':image_url,
            'image_role':'机身主图', 'image_copyright':'FUJIFILM',
            'params':params, 'spec_structure':structure,'spec_count':len(params),
            'fetched_at':datetime.now(timezone.utc).isoformat(),
            'availability_note':'官网当前产品导航收录；不代表中国实时库存'})
        # Save every item (stronger than the required ten-item checkpoint).
        dump(out/'goods.json', items)
        print(slug, structure, len(params), flush=True)
    dump(out/'goods.json', items)


PARENTS = {'x-h2':'100038651615', 'x-t5':'100104023155', 'x-s20':'100053477892',
           'x-t50':'10104665172451', 'x-e5':'10170879177338'}
LENS_SLUGS = {
    ('x-h2','1680套机'):'xf16-80mmf4-r-ois-wr',
    ('x-t5','1650套机'):'xf16-50mmf2.8-4.8-r-lm-wr',
    ('x-t5','1680套机'):'xf16-80mmf4-r-ois-wr',
    ('x-t5','23F2套机'):'xf23mmf2-r-wr',
    ('x-t5','35F2套机'):'xf35mmf2-r-wr',
    ('x-s20','XC35套机'):'xc35mmf2',
    ('x-s20','XF35套机'):'xf35mm-unconfirmed-aperture',
    ('x-s20','15-45套机'):'xc15-45mmf3.5-5.6-ois-pz',
    ('x-s20','16-50套机'):'16-50mm-unconfirmed-series',
    ('x-t50','XC35mmF2套机'):'xc35mmf2',
    ('x-t50','XC15-45mm套机'):'xc15-45mmf3.5-5.6-ois-pz',
    ('x-t50','XF16-50mm套机'):'xf16-50mmf2.8-4.8-r-lm-wr',
    ('x-e5','XF23mmF2.8套机'):'xf23mmf2.8-r-wr',
}


def kit_matrix(source):
    match = re.search(r'[\"\']salePropSeq[\"\']\s*:\s*', source)
    if not match:
        raise ValueError('No public salePropSeq version matrix')
    return json.JSONDecoder().raw_decode(source[match.end():])[0]


def add_kits(out):
    out = Path(out)
    f = Fetcher(out)
    bodies = json.loads((out/'goods.json').read_text())[:len(MODELS)]
    if {r['id'] for r in bodies} != {identity(m) for m in MODELS}:
        raise Stop('Incomplete body checkpoint; finish collect first')
    matrices = {}
    for slug, sku in PARENTS.items():
        url = f'https://item.m.jd.com/product/{sku}.html'
        source = f.get(url).decode()
        matrices[slug] = kit_matrix(source)
        dump(out/'kit-matrices.json', matrices)
    rows = list(csv.DictReader((ROOT/'docs/富士相机调研-20261027-evidence/kits.csv').open()))
    if len(rows) != 13:
        raise Stop('Expected exactly 13 researched kit versions')
    result = list(bodies)
    for row in rows:
        model, version, lens, sku, colors = row.values()
        slug = model.lower()
        matrix = json.dumps(matrices[slug], ensure_ascii=False)
        normalize = lambda text: re.sub(r'\s+', '', unicodedata.normalize('NFKC', text))
        if normalize(version) not in normalize(matrix):
            raise Stop(f'Researched kit absent from current parent matrix: {slug} {version}')
        lens_slug = LENS_SLUGS[(slug, version)]
        body = next(r for r in bodies if r['id'] == identity(slug))
        kit = dict(body)
        kit.update(id=identity(slug, lens_slug), name=body['name']+' '+version,
            params=body['params'] | {'版本':'套机', '包含镜头':lens},
            kit_version=version, lens_slug=lens_slug,
            kit_source_url=f'https://item.m.jd.com/product/{PARENTS[slug]}.html',
            lens_resolution='待确认' if 'unconfirmed' in lens_slug else '已归一',
            image_role='复用机身主图（非套机实物图）',
            kit_evidence='官方授权店父商品页版本矩阵；沿用调研 kits.csv，不表示厂商原厂包装认证')
        result.append(kit)
        dump(out/'goods.json',result)
    return result


def append_only(old, additions):
    old_ids = {r['id'] for r in old}
    if len({r['id'] for r in additions}) != len(additions):
        raise ValueError('Duplicate incoming ids')
    fresh = [r for r in additions if r['id'] not in old_ids]
    combined = old + fresh
    audit = {'old_count':len(old), 'added_fuji':len(fresh), 'new_count':len(combined),
             'existing_ids_missing':sorted(old_ids - {r['id'] for r in combined}),
             'existing_rows_unchanged':combined[:len(old)] == old,
             'old_unique_ids':len(old_ids)}
    return combined, audit


def publish(out, data_tree):
    out, tree = Path(out), Path(data_tree)
    goods_path, meta_path = tree/'public/goods.json', tree/'public/meta.json'
    old = json.loads(goods_path.read_text())
    additions = json.loads((out/'goods.json').read_text())
    if len(additions) != 24:
        raise ValueError('Refuse to publish incomplete collection; need 11 bodies + 13 kits')
    for row in additions:
        if (row['brand'], row['kind'], row['category'], row['price'], row['price_kind'], row['price_note']) != ('富士','machine','相机',None,'none','官网不公开人民币价'):
            raise ValueError('Invalid Fuji fields')
        if not row['params'] or not (out/'images'/Path(row['image']).name).exists():
            raise ValueError('Missing params/image')
    combined, audit = append_only(old, additions)
    meta = json.loads(meta_path.read_text())
    if meta['count'] != len(old):
        raise ValueError('Baseline metadata count mismatch')
    if audit['added_fuji']:
        meta['count'] = len(combined)
        meta.setdefault('brands',{})['富士'] = meta.get('brands',{}).get('富士',0) + audit['added_fuji']
        meta['by_kind'] = dict(Counter(r.get('kind') or 'unknown' for r in combined))
        meta['generated_at'] = datetime.now(timezone.utc).isoformat()
    if meta['with_price'] != sum(r.get('price') is not None for r in combined):
        raise ValueError('with_price mismatch')
    audit['with_price'] = meta['with_price']
    # Retain source provenance and images in data/, expose copies under public/ too.
    for name in ['goods.json','enumeration.json','kit-matrices.json','requests.json']:
        target = tree/'data/fuji'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(out/name,target)
    for row in additions:
        for target in [tree/row['image_local_path'], tree/'public'/row['image']]:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(out/'images'/Path(row['image']).name,target)
    dump(goods_path,combined)
    dump(meta_path,meta)
    dump(out/'publication-audit.json',audit)
    dump(tree/'data/fuji/publication-audit.json',audit)
    print(json.dumps(audit,ensure_ascii=False,indent=2))
    return audit


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['collect','kits','publish'])
    ap.add_argument('--out',default='data/fuji')
    ap.add_argument('--data-tree')
    args=ap.parse_args()
    Path(args.out).mkdir(parents=True, exist_ok=True)
    lock = (Path(args.out)/'run.lock').open('w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('STOP: another run owns this collection directory')
        return 1
    try:
        if args.command == 'collect':
            collect(args.out)
            add_kits(args.out)
        elif args.command == 'kits':
            add_kits(args.out)
        else:
            if not args.data_tree:
                ap.error('publish requires --data-tree (checked-out data branch)')
            publish(args.out,args.data_tree)
    except (Stop, ValueError) as exc:
        dump(Path(args.out)/'failure.json',{'error':str(exc),'at':datetime.now(timezone.utc).isoformat()})
        print(f'STOP: {exc}',flush=True)
        return 1
    (Path(args.out)/'failure.json').unlink(missing_ok=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
