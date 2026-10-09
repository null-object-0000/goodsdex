"""小米商城官方源（国内）。

两个源：
  - 移动端 mtop：参数最全（含发布日期、销量、口碑、问答）
  - PC 商品详情：图文详情、购买选项

注意移动端接口的三个坑（实测得出）：
  1. 必须 POST
  2. 4 个自定义头缺一不可
  3. body 是 mtop 数组格式 [{},{...}]，且带 gid 才返回完整数据

本模块返回 **Capture + Assertion 列表**，不返回用属性名去重的字典 ——
同值多源时每个来源都是独立佐证，必须全部保留。
"""
from __future__ import annotations
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from ..facts import Assertion, Availability, Capture, CaptureStatus

UA_PC = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
UA_M = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

MTOP_URL = "https://m.mi.com/mtop/xiaomishop/product/info"
MTOP_HEADERS = {
    "User-Agent": UA_M,
    "X-User-Agent": "channel/mishop platform/mishop.m",
    "mishop-client-id": "180100031051",
    "X-Mishop-App-Source": "front-RNWeb",
    "Mishop-Channel-Id": "channel",
    "Content-Type": "application/json",
    "Referer": "https://m.mi.com/",
    "Origin": "https://m.mi.com",
    "DToken": "",
}
SEARCH_URL = "https://api2.order.mi.com/search/index"
VIEW_URL = "https://api2.order.mi.com/product/view"
CATEGORY_URL = "https://www.mi.com/shop/category/list"

SRC_M = "mi_cn_mobile"
SRC_P = "mi_cn_pc"
PARSER_VERSION = "mi_cn-v2"

# PC 源限流熔断（进程内）：**连续** 429 达阈值即开路，避免持续无效请求。
# 成功会清零计数（见 fetch_pc），所以是"连续"而非"累计"。
PC_BREAKER_THRESHOLD = 5
_PC_BREAKER = {"fails": 0, "tripped": False, "reason": ""}


def breaker_status() -> dict:
    return dict(_PC_BREAKER)


def reset_breaker() -> None:
    _PC_BREAKER.update({"fails": 0, "tripped": False, "reason": ""})


def _get(url: str, timeout: int = 25, retries: int = 3,
         backoff: float = 1.5) -> str:
    """HTTP GET，带 429/5xx 退避重试。

    官方接口会限流（实测 HTTP 429）—— 这不是"没有数据"，
    必须重试；重试用尽才向上抛，由调用方记录为 transport_error。
    """
    import time
    last = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA_PC, "Referer": "https://www.mi.com/", "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                # 限流/临时故障 -> 指数退避后重试
                time.sleep(backoff ** (attempt + 1))
                continue
            raise
        except Exception as e:
            last = e
            if attempt < retries:
                time.sleep(backoff ** (attempt + 1))
                continue
            raise
    raise last


def _jsonp(raw: str) -> dict:
    m = re.match(r"^\w+\((.*)\);?\s*$", raw.strip(), re.S)
    return json.loads(m.group(1)) if m else {}


# ---------------- 分类与枚举 ----------------

def list_categories() -> dict[str, str]:
    """官方分类树 -> {分类名: 搜索关键词}

    实测教训：分类页有**两种**链接形式，且正则会漏：
      ① 侧边导航  <dd><a href=".../search?keyword=耳机">耳机</a></dd>
      ② 分类面板  <a href="..."><span class="text">吹风机</span></a>

    最初只认带 <span class="text"> 的形式，漏掉 10 个大类
    （手机/电视/笔记本/平板/穿戴/耳机/家电/路由器/音箱/配件）。

    后又发现正则本身脆弱：`dd class="nav"`、`span class="text active"`、
    实体编码 `&amp;page=2` 都会导致漏解析或关键词污染。
    改用 HTMLParser —— 结构解析交给解析器，不靠正则猜。

    额外做**健全性检查**：分类数骤降或大类缺失时抛异常，
    不返回一个"看起来成功"的短字典。
    """
    d = _get(CATEGORY_URL)
    tree: dict[str, str] = {}

    class _CatParser(HTMLParser):
        """收集 <a href> 的可见文本与其 keyword 参数。

        两种形式都覆盖：<dd><a>文本</a> 与 <a><span class="text">文本</span></a>
        """

        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.in_dd = 0
            self.cur_href: str | None = None
            self.cur_text: list[str] = []
            self.results: list[tuple[str, str]] = []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "dd":
                self.in_dd += 1
            if tag == "a" and a.get("href"):
                self.cur_href = a["href"]
                self.cur_text = []
                self.in_dd = self.in_dd or 0

        def handle_endtag(self, tag):
            if tag == "dd" and self.in_dd:
                self.in_dd -= 1
            if tag == "a" and self.cur_href is not None:
                txt = "".join(self.cur_text).strip()
                if txt and "keyword=" in self.cur_href:
                    self.results.append((self.cur_href, txt))
                self.cur_href = None
                self.cur_text = []

        def handle_data(self, data):
            if self.cur_href is not None and data.strip():
                self.cur_text.append(data.strip())

    p = _CatParser()
    p.feed(d)
    for href, name in p.results:
        kw = _keyword_from_href(href)
        if kw and name:
            tree.setdefault(name, kw)

    # 健全性检查：大类缺失说明页面结构变了
    expected = {"手机", "耳机", "电视", "笔记本", "平板"}
    missing = expected - set(tree)
    if len(tree) < 40 or missing:
        raise RuntimeError(
            f"分类解析异常：仅得 {len(tree)} 个分类，缺少 {sorted(missing)}。"
            f"页面结构可能已变化，请检查 _get(CATEGORY_URL) 的返回。")
    return tree


def _keyword_from_href(href: str) -> str:
    """从 search?keyword=xxx 提取关键词。

    用 parse_qs 而非 split —— 后者会把 `&page=2` 一并当成关键词
    （实测：'耳机&amp;page=2'）。
    """
    try:
        q = urllib.parse.urlparse(href).query
        vals = urllib.parse.parse_qs(q).get("keyword") or []
        return vals[0].strip() if vals else ""
    except Exception:
        return ""


def enumerate_products(query: str, max_pages: int = 20, page_size: int = 20,
                       pause: float = 0.3) -> dict:
    """分页枚举商品。

    返回 {items: [...], discovery: {...}}。discovery 记录枚举范围与完整性 ——
    不能把短列表当成"这个分类只有这些商品"。
    """
    import time
    seen, rows, page = set(), [], 1
    last_total = None
    empty_pages = 0
    stop_reason = "unknown"
    while page <= max_pages:
        q = {"query": query, "page_index": page, "page_size": page_size,
             "filter_tag": 0, "main_sort": 0, "province_id": "", "city_id": "",
             "sort_by": "asc", "callback": "cb"}
        try:
            raws = _get(f"{SEARCH_URL}?{urllib.parse.urlencode(q)}")
            d = _jsonp(raws)
        except Exception as e:
            stop_reason = f"error: {e}"
            break
        # **校验业务状态与 schema** —— 不能把接口报错当成"官方没有在售"
        # （Codex 评审指认：{code:500,data:{total:57}} 曾被判为 no_sellable_items）
        if not isinstance(d, dict) or not d:
            stop_reason = "parse_error: 响应无法解析（非 JSONP 或空）"
            break
        code = d.get("code")
        if code is not None and code != 0:
            stop_reason = f"api_error: code={code} msg={d.get('message')}"
            break
        data = d.get("data")
        if not isinstance(data, dict):
            stop_reason = "schema_error: data 不是对象"
            break
        if "pc_list" not in data:
            stop_reason = "schema_error: 缺少 pc_list 字段"
            break
        groups, total = data.get("pc_list") or [], data.get("total")
        if total is not None:
            last_total = total
        if not groups:
            # total 是全局匹配数，pc_list 才是本页可售结果 ——
            # total>0 而 pc_list 空表示该词下没有在售商品（下架/售罄），
            # 不是"还能翻页"。容忍一页空响后停止。
            empty_pages += 1
            if empty_pages >= 2 or page == 1:
                stop_reason = "no_sellable_items" if last_total else "empty_page"
                break
            page += 1
            continue
        empty_pages = 0
        new = 0
        for g in groups:
            pid = g.get("product_id")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            cl = g.get("commodity_list") or [{}]
            rows.append({
                "pid": pid,
                "name": cl[0].get("name", ""),
                "price": cl[0].get("price"),
                "image": cl[0].get("image"),
                # 保留全部变体：product_id 是产品级，commodity_id 才是可购买单位
                "variants": [{"commodity_id": c.get("commodity_id"),
                              "name": c.get("name"),
                              "price": c.get("price"),
                              "market_price": c.get("market_price"),
                              "image": c.get("image")} for c in cl],
            })
            new += 1
        if last_total is not None and len(rows) >= last_total:
            stop_reason = "reached_total"
            break
        if new == 0:
            stop_reason = "no_new_items"
            break
        page += 1
        time.sleep(pause)
    else:
        stop_reason = "max_pages_reached"

    if stop_reason.startswith(("api_error", "parse_error", "schema_error", "error")):
        # **失败绝不装成"官方没有"** —— 这是核心承诺
        completeness = "failed"
    elif stop_reason == "no_sellable_items":
        # 明确：搜索命中 total 条，但没有在售商品
        completeness = "no_sellable_items"
    elif last_total is not None and len(rows) >= last_total:
        completeness = "complete"
    elif rows and stop_reason in ("max_pages_reached", "no_new_items"):
        completeness = "partial"      # 达到页数上限或分页异常，不能声称完整
    elif rows:
        completeness = "partial"
    else:
        completeness = "unknown"

    return {
        "items": rows,
        "discovery": {
            "query": query, "pages_fetched": page, "page_size": page_size,
            "total_reported": last_total, "found": len(rows),
            "stop_reason": stop_reason, "completeness": completeness,
            "universe": "中国大陆小米商城本次搜索可发现的商品",
        },
    }


# ---------------- 移动端 ----------------

def _mtop_call(pid: str, gid: str | None = None) -> tuple[dict, str, int, str]:
    """返回 (解析后 JSON, 原始响应文本, http 状态, 错误)"""
    body = [{}, ({"productId": pid, "gid": gid} if gid else {"productId": pid})]
    body_str = json.dumps(body, ensure_ascii=False)
    req = urllib.request.Request(MTOP_URL, data=body_str.encode(), headers=MTOP_HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read().decode("utf-8", "ignore")
        return json.loads(raw), raw, resp.status, ""
    except Exception as e:
        return {}, "", getattr(e, "code", 0) or 0, str(e)


def fetch_mobile(pid: str) -> tuple[list[Capture], list[Assertion]]:
    """移动端采集 -> (captures, assertions)"""
    captures: list[Capture] = []
    out: list[Assertion] = []

    d, raw, http, err = _mtop_call(pid)
    if err or d.get("code") != 0:
        status = CaptureStatus.TRANSPORT_ERROR if err else CaptureStatus.SOURCE_ERROR
        captures.append(Capture.make(
            SRC_M, MTOP_URL, raw, status=status, http_status=http,
            error=err or str(d.get("message")), method="POST",
            parser_version=PARSER_VERSION))
        return captures, out

    cap0 = Capture.make(SRC_M, MTOP_URL, raw, method="POST", http_status=http,
                        parser_version=PARSER_VERSION)
    captures.append(cap0)

    # 带 gid 的第二次请求更全；失败则降级用第一次，标记 PARTIAL
    gid = ((d.get("data") or {}).get("product") or {}).get("defaultGid")
    if gid:
        d2, raw2, http2, err2 = _mtop_call(pid, gid)
        if not err2 and d2.get("code") == 0:
            d, raw = d2, raw2
            cap0 = Capture.make(SRC_M, f"{MTOP_URL}?gid={gid}", raw2, method="POST",
                                http_status=http2, parser_version=PARSER_VERSION)
            # **必须把新快照加入 captures** —— 否则断言引用的 capture_id
            # 在 captures 里找不到，溯源链断裂（实测曾导致 77% 断言悬空）
            captures.append(cap0)
        else:
            cap0.status = CaptureStatus.PARTIAL
            cap0.error = f"gid 请求失败，降级使用首次结果: {err2 or d2.get('message')}"
    cid = cap0.capture_id

    # 自检：断言引用的快照必须在 captures 里
    assert any(c.capture_id == cid for c in captures), \
        f"断言的 capture_id {cid} 不在 captures 中，溯源链会断裂"

    data = d.get("data") or {}
    prod = data.get("product") or {}
    gl = (data.get("goodsInfo") or {}).get("goodsList") or []
    g = gl[0] if gl else {}

    def A(attr, value, locator, ui="", avail=Availability.PROVIDED, **kw):
        return Assertion(assertion_id=f"{cid}:{attr}", subject_id=pid, capture_id=cid,
                         source=SRC_M, attribute=attr, raw_value=value, locator=locator,
                         ui_location=ui, page="移动端商品详情页",
                         availability=avail, parser_version=PARSER_VERSION, **kw)

    if prod.get("name"):
        out.append(A("name", prod["name"].strip(), "$.data.product.name", "商品名"))
    if prod.get("shortTitle"):
        out.append(A("short_title", prod["shortTitle"], "$.data.product.shortTitle", "副标题"))
    out.append(A("sell_points", prod.get("sellPointList") or [],
                 "$.data.product.sellPointList", "卖点"))
    out.append(A("gid", prod.get("defaultGid"), "$.data.product.defaultGid"))
    if g.get("commodityId"):
        out.append(A("commodity_id", g["commodityId"],
                     "$.data.goodsInfo.goodsList[0].commodityId"))
    if g.get("sku"):
        out.append(A("sku", g["sku"], "$.data.goodsInfo.goodsList[0].sku"))
    if g.get("price"):
        out.append(A("price", g["price"], "$.data.goodsInfo.goodsList[0].price", "现价"))
    if g.get("marketPrice"):
        out.append(A("market_price", g["marketPrice"],
                     "$.data.goodsInfo.goodsList[0].marketPrice", "划线价"))
    if g.get("imgUrl"):
        out.append(A("img_url", g["imgUrl"], "$.data.goodsInfo.goodsList[0].imgUrl"))
    car = [c.get("imgUrl") for c in (g.get("carouselList") or []) if c.get("imgUrl")]
    if car:
        # raw_value 是提取后的 URL 列表，locator 指向**源列表**（可解析）
        out.append(A("carousel", car,
                     "$.data.goodsInfo.goodsList[0].carouselList", "轮播图"))

    colors, attrs = [], {}
    for a in ((data.get("saleAttributeInfo") or {}).get("saleAttributeList") or []):
        vals = [v.get("attributeValueName") for v in a.get("attributeValueList") or []]
        attrs[a.get("attributeName")] = vals
        if a.get("attributeName") == "颜色":
            colors = vals
    if attrs:
        out.append(A("attrs", attrs, "$.data.saleAttributeInfo.saleAttributeList"))
    if colors:
        out.append(A("colors", colors,
                     "$.data.saleAttributeInfo.saleAttributeList", "可选颜色"))

    bs = data.get("buyerShow") or {}
    if bs.get("total"):
        out.append(A("evaluate_total", bs["total"], "$.data.buyerShow.total", "评论数"))
    if bs.get("realTotal") is not None:
        out.append(A("evaluate_real", bs["realTotal"], "$.data.buyerShow.realTotal", "评论数"))
    if bs.get("tags"):
        out.append(A("review_tags", bs["tags"], "$.data.buyerShow.tags[]", "大家评价"))
    if bs.get("imgs"):
        out.append(A("buyer_imgs", bs["imgs"][:12], "$.data.buyerShow.imgs[]", "买家秀"))
    ask = data.get("askAll") or {}
    if ask.get("total"):
        out.append(A("qa_total", ask["total"], "$.data.askAll.total", "问大家"))
    if ask.get("items"):
        out.append(A("qa_items", ask["items"], "$.data.askAll.items[]", "问大家"))

    # 关键参数 —— 逐条断言，locator 保留**原始数组索引**
    params = (g.get("classParameters") or {}).get("list") or []
    for idx, item in enumerate(params):
        name, value = item.get("name"), item.get("value")
        if not name:
            continue
        avail = Availability.PROVIDED if value not in (None, "") else Availability.SOURCE_EMPTY
        out.append(A(name, value,
                     f"$.data.goodsInfo.goodsList[0].classParameters.list[{idx}]",
                     "关键参数", avail))
    if not params:
        # 空参数列表是**有效采集结果**，不是失败，也不能推断原因
        out.append(A("_params_empty", True,
                     "$.data.goodsInfo.goodsList[0].classParameters.list",
                     "关键参数", Availability.SOURCE_EMPTY))
    return captures, out


# ---------------- PC ----------------

def fetch_pc(pid: str) -> tuple[list[Capture], list[Assertion]]:
    url = f"{VIEW_URL}?product_id={pid}&version=2"
    captures: list[Capture] = []
    out: list[Assertion] = []
    # 限流熔断：连续多次 429 说明已被 IP 级限流，继续打只会更糟。
    # 标为 rate_limited（区别于"源未提供"），并让调用方跳过后续 PC 请求。
    if _PC_BREAKER["tripped"]:
        captures.append(Capture.make(
            "mi_cn_pc", url, "", status=CaptureStatus.RATE_LIMITED,
            error=f"circuit open: {_PC_BREAKER['reason']}"))
        return captures, out
    try:
        raw = _get(url)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            _PC_BREAKER["fails"] += 1
            if _PC_BREAKER["fails"] >= PC_BREAKER_THRESHOLD:
                _PC_BREAKER["tripped"] = True
                _PC_BREAKER["reason"] = f"连续 {_PC_BREAKER['fails']} 次 429"
            captures.append(Capture.make("mi_cn_pc", url, "",
                                         status=CaptureStatus.RATE_LIMITED,
                                         error=f"HTTP 429 Too Many Requests"))
            return captures, out
        raise
    # 成功即清零 —— 否则熔断判据实际是"累计 5 次"而非"连续 5 次"
    # （Codex 评审指认：429 后成功一次仍是 fails=1）
    _PC_BREAKER["fails"] = 0
    caps, asserts = _parse_pc(raw, url, pid)
    captures.extend(caps)
    out.extend(asserts)
    return captures, out


def _parse_pc(raw: str, url: str, pid: str) -> tuple[list[Capture], list[Assertion]]:
    """解析 PC 商品详情响应 -> (captures, assertions)"""
    captures: list[Capture] = []
    out: list[Assertion] = []
    try:
        d = json.loads(raw)
    except Exception as e:
        captures.append(Capture.make(SRC_P, url, raw, status=CaptureStatus.PARSE_ERROR,
                                     error=str(e), parser_version=PARSER_VERSION))
        return captures, out
    if d.get("code") != 200:
        captures.append(Capture.make(SRC_P, url, raw, status=CaptureStatus.SOURCE_ERROR,
                                     http_status=d.get("code"), error=str(d.get("msg")),
                                     parser_version=PARSER_VERSION))
        return captures, out
    cap = Capture.make(SRC_P, url, raw, parser_version=PARSER_VERSION)
    captures.append(cap)
    cid = cap.capture_id

    def A(attr, value, locator, ui="", **kw):
        return Assertion(assertion_id=f"{cid}:{attr}", subject_id=pid, capture_id=cid,
                         source=SRC_P, attribute=attr, raw_value=value, locator=locator,
                         ui_location=ui, page="PC 商品详情页",
                         parser_version=PARSER_VERSION, **kw)

    pv = d.get("data") or {}
    pi = pv.get("product_info") or {}
    gl = pv.get("goods_list") or []
    gi = (gl[0] or {}).get("goods_info", {}) if gl else {}
    if pi.get("product_desc"):
        out.append(A("desc", pi["product_desc"], "$.data.product_info.product_desc", "商品简介"))
    if gi.get("price"):
        out.append(A("pc_price", gi["price"], "$.data.goods_list[0].goods_info.price", "现价"))
    if gi.get("market_price"):
        out.append(A("pc_market_price", gi["market_price"],
                     "$.data.goods_list[0].goods_info.market_price", "划线价"))
    if pv.get("buy_option"):
        out.append(A("buy_options", pv["buy_option"], "$.data.buy_option[]", "选择规格"))
    tabs, imgs = [], []
    for tab in ((pv.get("extend_info") or {}).get("desc_tabs_view") or []):
        tabs.append(tab.get("name"))
        for c in (tab.get("tab_content") or []):
            p = c.get("plain_view") or {}
            if p.get("img"):
                imgs.append({"tab": tab.get("name"), "img": p["img"],
                             "w": p.get("w"), "h": p.get("h")})
    if tabs:
        # locator 指向**整个列表**（raw_value 就是列表），不是某个元素。
        # 原写法 `desc_tabs_view[].name` 是"遍历"语义，不是合法可解析路径。
        out.append(A("pc_tabs", tabs, "$.data.extend_info.desc_tabs_view", "商品详情"))
    if imgs:
        out.append(A("pc_imgs", imgs,
                     "$.data.extend_info.desc_tabs_view", "商品详情"))
    return captures, out


# ---------------- 兼容层：断言 -> 旧式 dict ----------------
# 新代码请直接用 fetch_mobile / fetch_pc；这两个仅供过渡期使用。

def _assertions_to_legacy(pairs, site: str, api: str) -> dict:
    from ..model import Provenance
    out = {}
    for a in pairs:
        out[a.attribute] = (a.raw_value, Provenance(
            source=a.source, site=site, page=a.page, ui_location=a.ui_location,
            api=api, json_path=a.locator, raw_field=a.attribute))
    return out


def fetch_mobile_legacy(pid: str) -> dict:
    caps, assertions = fetch_mobile(pid)
    return _assertions_to_legacy(assertions, "m.mi.com",
                                 "POST /mtop/xiaomishop/product/info")


def fetch_pc_legacy(pid: str) -> dict:
    caps, assertions = fetch_pc(pid)
    return _assertions_to_legacy(assertions, "www.mi.com",
                                 "GET api2.order.mi.com/product/view")
