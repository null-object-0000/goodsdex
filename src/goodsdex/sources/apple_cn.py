"""Apple 中国大陆官方商店：从页面实际 JSON bootstrap 枚举规格，不执行远端 JS。

价格取 currentPrice.raw_amount，绝不取分期、抵扣后金额或首页起售价。
Watch 表壳及 Mac 可配置入口的价格仍明确标 starting，不声称穷举表带/CTO。
"""

from __future__ import annotations

import gzip
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path

from ..facts import Capture, CaptureStatus, Assertion
from ..identity import make_product_id, make_variant_id

SOURCE = "apple_cn"
VERSION = "apple-cn-v1"
ORIGIN = "https://www.apple.com.cn"
FAMILIES = {
    "iphone": ("手机", "/shop/buy-iphone", "/iphone/"),
    "ipad": ("平板", "/shop/buy-ipad", "/ipad/"),
    "mac": ("电脑", "/shop/buy-mac", "/mac/"),
    "watch": ("手表", "/shop/buy-watch", "/watch/"),
    "airpods": ("耳机", "/airpods/"),
    "homepod": ("音箱", "/homepod/"),
    "airtag": ("配件", "/airtag/"),
    "vision": ("空间计算设备", "/shop/buy-vision", "/apple-vision-pro/"),
}


def text(value):
    value = re.sub(
        r"<(?:sup|as-footnote)\b[^>]*>.*?</(?:sup|as-footnote)>",
        "",
        str(value or ""),
        flags=re.S,
    )
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def links_in(body):
    p = Links()
    p.feed(body)
    return p.links


def official_url(url):
    p = urllib.parse.urlsplit(urllib.parse.urljoin(ORIGIN, html.unescape(url)))
    if p.scheme != "https" or p.hostname != "www.apple.com.cn" or p.port:
        raise ValueError("只接受 Apple 中国大陆官方 HTTPS 页面")
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, "", ""))


def shop_target(url):
    """仅发现官方实际链接；goto 是官网路由，保留它让服务器解析。"""
    try:
        url = official_url(url)
    except ValueError:
        return None
    path = urllib.parse.urlsplit(url).path
    m = re.fullmatch(r"/shop/buy-([a-z]+)/([^/]+)(?:/.*)?", path)
    if m and m[1] in FAMILIES:
        return m[1], ORIGIN + f"/shop/buy-{m[1]}/{m[2]}"
    m = re.fullmatch(r"/cn/shop/goto/buy_([a-z]+)/([^/]+)(?:/.*)?", path)
    if m and m[1] in FAMILIES:
        return m[1], ORIGIN + f"/cn/shop/goto/buy_{m[1]}/{m[2]}"
    return None


class CNRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # 不跨区、不带 cookie，也不让官方重定向变成任意 URL 抓取。
        official_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, timeout=25):
    url = official_url(url)
    cap = Capture.make(SOURCE, url, parser_version=VERSION)
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 GoodsDex/1.0",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept-Encoding": "identity",
            },
        )
        with urllib.request.build_opener(CNRedirect()).open(req, timeout=timeout) as r:
            official_url(r.url)
            raw = r.read()
            body = (gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw).decode(
                "utf-8"
            )
            return Capture.make(
                SOURCE, r.url, body, http_status=r.status, parser_version=VERSION
            )
    except urllib.error.HTTPError as exc:
        cap.http_status = exc.code
        cap.status = (
            CaptureStatus.RATE_LIMITED
            if exc.code == 429
            else CaptureStatus.NOT_FOUND
            if exc.code == 404
            else CaptureStatus.TRANSPORT_ERROR
        )
        cap.error = str(exc)
    except Exception as exc:
        cap.status = CaptureStatus.TRANSPORT_ERROR
        cap.error = f"{type(exc).__name__}: {exc}"
    return cap


def bootstrap(body):
    # JSONDecoder 只读取一个 JSON 值；不 eval，不把 JS 语法当 JSON 修补。
    for m in re.finditer(r"\bproductSelectionData\s*:\s*", body):
        try:
            data, _ = json.JSONDecoder().raw_decode(body[m.end() :])
            if isinstance(data, dict) and isinstance(data.get("products"), list):
                return data
        except ValueError:
            pass
    raise ValueError(
        "未找到可识别的官方 productSelectionData，不能宣称商品为空或已下架"
    )


def amount(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = Decimal(str(value))
        if n.is_finite() and n > 0 and n <= 10000000:
            return int(n) if n == n.to_integral_value() else float(n)
    except InvalidOperation:
        pass
    return None


def _assert(cap, subject, attribute, raw_value, locator, qualifiers=None):
    key = f"{cap.capture_id}|{subject}|{attribute}|{locator}"
    return Assertion(
        hashlib.sha256(key.encode()).hexdigest()[:16],
        subject,
        cap.capture_id,
        SOURCE,
        attribute,
        raw_value,
        locator=locator,
        qualifiers=qualifiers or {},
        parser_version=VERSION,
    )


def _name(body):
    title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    name = text(title[1]) if title else ""
    return re.sub(
        r"^(?:选购|购买)\s*", "", re.sub(r"\s*[-–] Apple.*$", "", name)
    ).strip()


def parse_product(cap, family):
    data = bootstrap(cap.response_raw)
    display_key = (
        "mainDisplayValues" if "mainDisplayValues" in data else "displayValues"
    )
    display = data.get(display_key) or {}
    page_name = _name(cap.response_raw)
    slug = urllib.parse.urlsplit(cap.url).path.split("/")[-1]
    records = []
    for index, product in enumerate(data["products"]):
        if not isinstance(product, dict):
            continue
        sku = (
            product.get("partNumber")
            or product.get("btrOrFdPartNumber")
            or product.get("part")
        )
        if not sku or not re.fullmatch(r"[A-Z0-9]+CH/[A-Z0-9]+", sku):
            # 可配置 Mac 没有唯一购买料号，不造 SKU；由基准预配置料号代表。
            continue
        family_id = (
            product.get("familyType")
            or product.get("aosContainerPartNumber")
            or re.sub(r"[^a-z0-9]+", "-", page_name.lower()).strip("-")
            or slug
        )
        parent = make_product_id("CN", SOURCE, family_id)
        vid = make_variant_id("CN", SOURCE, sku)
        prefix = (
            f"html:PRODUCT_SELECTION_BOOTSTRAP.productSelectionData.products[{index}]"
        )
        raw_dims = product.get("dimensions") or {
            k: v
            for k, v in product.items()
            if "dimension" in k.lower() and isinstance(v, str)
        }
        dims = {}
        dim_asserts = []
        for key, value in raw_dims.items():
            label = display.get(key, {}).get(value, {})
            pretty = (
                text(label.get("value") or label.get("header") or value)
                if isinstance(label, dict)
                else str(value)
            )
            dims[key] = {"value": value, "label": pretty}
            dim_asserts.append(
                _assert(
                    cap,
                    vid,
                    key,
                    value,
                    prefix
                    + (
                        f".dimensions[{json.dumps(key)}]"
                        if product.get("dimensions")
                        else f"[{json.dumps(key)}]"
                    ),
                )
            )
        model = dims.get("dimensionScreensize", {}).get("label", "")
        name = (
            re.split(r"\s+\d+(?:\.\d+)?\s*英寸", model)[0]
            if model.startswith("iPhone")
            else page_name
        )
        if not name:
            raise ValueError("官方商品名缺失")
        qualifiers = {"market": "CN", "currency": "CNY", "part_number": sku}
        price_key = (
            product.get("fullPrice") or product.get("priceKey") or product.get("price")
        )
        price_entry = (display.get("prices") or {}).get(price_key) or {}
        price = None
        # 有货币声明时必须是人民币；不能把其他区价格接过来。
        if price_entry.get("priceCurrency", "CNY") == "CNY":
            valid = price_entry.get("validProducts")
            if not valid or sku in valid:
                price = amount(
                    (price_entry.get("currentPrice") or {}).get("raw_amount")
                )
        price_kind = "starting" if family in ("watch", "mac") else "sku"
        vals = {"name": name, "price": price, "part_number": sku, "variant_attrs": dims}
        name_locator = (
            f"html:PRODUCT_SELECTION_BOOTSTRAP.productSelectionData.{display_key}.dimensionScreensize[{json.dumps(raw_dims.get('dimensionScreensize'))}].value"
            if model.startswith("iPhone")
            else "html:document.title"
        )
        title_match = re.search(
            r"<title[^>]*>(.*?)</title>", cap.response_raw, re.S | re.I
        )
        raw_name = (
            display.get("dimensionScreensize", {})
            .get(raw_dims.get("dimensionScreensize"), {})
            .get("value")
            if model.startswith("iPhone")
            else title_match[1]
        )
        name_assertion = _assert(cap, vid, "name", raw_name, name_locator)
        name_assertion.normalized_value = name
        name_assertion.normalization_rule_version = VERSION
        sku_field = (
            "partNumber"
            if product.get("partNumber")
            else "btrOrFdPartNumber"
            if product.get("btrOrFdPartNumber")
            else "part"
        )
        assertions = [
            name_assertion,
            _assert(cap, vid, "part_number", sku, prefix + "." + sku_field),
            *dim_asserts,
        ]
        if price is not None:
            assertions.append(
                _assert(
                    cap,
                    vid,
                    "price",
                    price_entry["currentPrice"]["raw_amount"],
                    f"html:PRODUCT_SELECTION_BOOTSTRAP.productSelectionData.{display_key}.prices[{json.dumps(price_key)}].currentPrice.raw_amount",
                    {**qualifiers, "price_kind": price_kind},
                )
            )
            assertions[-1].normalized_value = price
            assertions[-1].normalization_rule_version = VERSION
        image_key = product.get("imageKey")
        image = (data.get("imageDictionary") or {}).get(image_key) or {}
        sources = image.get("sources") or []
        image_url = sources[0].get("srcSet", "").split(" ")[0] if sources else ""
        if image_url:
            vals["img_url"] = image_url
            assertions.append(
                _assert(
                    cap,
                    vid,
                    "img_url",
                    image_url,
                    f"html:PRODUCT_SELECTION_BOOTSTRAP.productSelectionData.imageDictionary[{json.dumps(image_key)}].sources[0].srcSet",
                )
            )
        if product.get("productConfiguration"):
            vals["configuration_codes"] = product["productConfiguration"]
            assertions.append(
                _assert(
                    cap,
                    vid,
                    "configuration_codes",
                    product["productConfiguration"],
                    prefix + ".productConfiguration",
                )
            )
        product_info = {
            "product_id": parent,
            "variant_id": vid,
            "name": name,
            "brand": "Apple",
            "market": "CN",
            "source": SOURCE,
            "category": FAMILIES[family][0],
            "family": family,
            "kind": "accessory" if family == "airtag" else "machine",
            "part_number": sku,
            "source_url": cap.url,
            "currency": "CNY",
            "price_kind": price_kind,
            "price_status": "provided" if price is not None else "not_collected",
            "price_fetched_at": cap.fetched_at if price is not None else None,
            "variant_attrs": dims,
        }
        records.append(
            {
                "product": product_info,
                "view": {
                    "values": vals,
                    "selected_from": {a.attribute: a.assertion_id for a in assertions},
                },
                "captures": [cap.to_dict()],
                "assertions": [a.to_dict() for a in assertions],
                "fetched_at": cap.fetched_at,
                "discovery": {
                    "scope": "official_CN_preconfigured_SKUs",
                    "completeness": "partial",
                    "excludes": [
                        "CTO combinations",
                        "watch band combinations",
                        "accessory catalogue",
                        "historical products not currently listed",
                    ],
                },
            }
        )
    if not records:
        raise ValueError(
            "页面未解析出中国大陆购买料号；保留上次结果，不把解析失败当作空目录"
        )
    # 同页重复声明只保留同一料号的一条，跨颜色/容量绝不合并。
    return list({r["product"]["variant_id"]: r for r in records}.values())


def externalize(cap, raw_dir):
    """原始 HTML 保存完整内容；证据引用只留预览和 SHA，绝不截断冒充完整。"""
    if not cap.response_raw:
        return
    digest = hashlib.sha256(cap.response_raw.encode()).hexdigest()
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / (digest + ".html")
    target.write_text(cap.response_raw, encoding="utf-8")
    cap.raw_ref = str(target)
    cap.response_raw = f"<externalized:{digest}>"


def discover(families=None, transport=fetch, pause=0.15):
    wanted = list(families or FAMILIES)
    captures = []
    targets = {}
    specs = set()
    marketing = set()
    for family in wanted:
        if family not in FAMILIES:
            raise ValueError(f"不支持的 Apple 系列: {family}")
        for seed in FAMILIES[family][1:]:
            cap = transport(ORIGIN + seed)
            captures.append(cap)
            if cap.status != CaptureStatus.SUCCESS:
                continue
            for link in links_in(cap.response_raw):
                target = shop_target(link)
                if target and target[0] == family:
                    targets[target[1]] = family
                try:
                    url = official_url(link)
                    if re.fullmatch(r"/[a-z0-9-]+/", urllib.parse.urlsplit(url).path):
                        marketing.add(url)
                    if url.endswith(("/specs/", "/tech-specs/")):
                        specs.add(url)
                except ValueError:
                    pass
            if pause:
                time.sleep(pause)
    return targets, captures, sorted(specs), sorted(marketing)


class SpecTree(HTMLParser):
    """仅保留有语义的官方规格表行；表格列不拼成单个产品参数。"""

    VOID = {
        "img",
        "br",
        "input",
        "meta",
        "link",
        "hr",
        "source",
        "wbr",
        "area",
        "embed",
        "param",
        "track",
        "col",
        "base",
    }

    def __init__(self):
        super().__init__()
        self.root = {"attrs": {}, "children": [], "parts": []}
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": [], "parts": []}
        self.stack[-1]["children"].append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].get("tag") == tag:
                del self.stack[i:]
                break

    def handle_data(self, value):
        if any(
            n.get("tag") in ("script", "style", "sup", "as-footnote")
            for n in self.stack
        ):
            return
        for n in self.stack:
            n["parts"].append(value)


def _nodes(node):
    yield node
    for child in node["children"]:
        yield from _nodes(child)


def parse_specs(body):
    tree = SpecTree()
    tree.feed(body)
    tables = [
        n
        for n in _nodes(tree.root)
        if "techspecs" in n["attrs"].get("class", "").split()
    ]
    if not tables:
        return None
    table = tables[0]
    columns = []
    rows = []
    for node in _nodes(table):
        role = node["attrs"].get("role", "")
        if role == "columnheader":
            value = text(" ".join(node["parts"]))
            if value:
                columns.append(value)
        if role != "row":
            continue
        headers = [n for n in _nodes(node) if n["attrs"].get("role") == "rowheader"]
        cells = [n for n in _nodes(node) if n["attrs"].get("role") == "cell"]
        if headers and cells:
            rows.append(
                {
                    "label": text(" ".join(headers[0]["parts"])),
                    "cells": [text(" ".join(n["parts"])) for n in cells],
                }
            )
    return {"scope": "family_table", "columns": columns, "rows": rows} if rows else None


def specs_target(records, urls):
    if not records:
        return None
    p = records[0]["product"]
    slug = urllib.parse.urlsplit(p["source_url"]).path.split("/")[-1]
    exact = [u for u in urls if urllib.parse.urlsplit(u).path.split("/")[1] == slug]
    if len(exact) == 1:
        return exact[0]
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    exact = [
        u
        for u in urls
        if norm(urllib.parse.urlsplit(u).path.split("/")[1]) == norm(p["name"])
    ]
    return exact[0] if len(exact) == 1 else None


def marketing_target(records, urls):
    if not records:
        return None
    p = records[0]["product"]
    slug = urllib.parse.urlsplit(p["source_url"]).path.split("/")[-1]
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    matches = [u for u in urls if urllib.parse.urlsplit(u).path.strip("/") == slug]
    if len(matches) == 1:
        return matches[0]
    matches = [
        u for u in urls if norm(urllib.parse.urlsplit(u).path) == norm(p["name"])
    ]
    return matches[0] if len(matches) == 1 else None
