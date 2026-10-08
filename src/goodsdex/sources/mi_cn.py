"""小米商城官方源（国内）。

两个源：
  - 移动端 mtop：参数最全（含发布日期、销量、口碑、问答）
  - PC 商品详情：图文详情、购买选项

注意移动端接口的三个坑（实测得出）：
  1. 必须 POST
  2. 4 个自定义头缺一不可
  3. body 是 mtop 数组格式 [{},{...}]，且带 gid 才返回完整数据
"""
from __future__ import annotations
import json
import re
import urllib.parse
import urllib.request

from ..model import Provenance

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


def _get(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA_PC, "Referer": "https://www.mi.com/", "Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def _jsonp(raw: str) -> dict:
    m = re.match(r"^\w+\((.*)\);?\s*$", raw.strip(), re.S)
    return json.loads(m.group(1)) if m else {}


# ---------------- 分类与枚举 ----------------

def list_categories() -> dict[str, str]:
    """官方分类树 -> {分类名: 搜索关键词}"""
    d = _get(CATEGORY_URL)
    items = re.findall(
        r'<a[^>]*href="([^"]*)"[^>]*>\s*(?:<img[^>]*>\s*)?<span class="text">([^<]+)</span>', d)
    tree = {}
    for u, n in items:
        if "search?keyword=" in u:
            tree[n.strip()] = urllib.parse.unquote(u.split("keyword=")[-1])
    return tree


def enumerate_products(query: str, max_pages: int = 20, page_size: int = 20,
                       pause: float = 0.3) -> list[dict]:
    """分页枚举商品，返回 [{pid, name, price, image}]"""
    import time
    seen, rows, page = set(), [], 1
    while page <= max_pages:
        q = {"query": query, "page_index": page, "page_size": page_size,
             "filter_tag": 0, "main_sort": 0, "province_id": "", "city_id": "",
             "sort_by": "asc", "callback": "cb"}
        try:
            d = _jsonp(_get(f"{SEARCH_URL}?{urllib.parse.urlencode(q)}"))
        except Exception:
            break
        data = d.get("data") or {}
        groups, total = data.get("pc_list", []), data.get("total", 0)
        if not groups:
            break
        new = 0
        for g in groups:
            pid = g.get("product_id")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            cl = g.get("commodity_list") or [{}]
            rows.append({"pid": pid, "name": cl[0].get("name", ""),
                         "price": cl[0].get("price"), "image": cl[0].get("image")})
            new += 1
        if len(rows) >= total or new == 0:
            break
        page += 1
        time.sleep(pause)
    return rows


# ---------------- 移动端 ----------------

def _mtop(pid: str, gid: str | None = None) -> dict:
    body = [{}, ({"productId": pid, "gid": gid} if gid else {"productId": pid})]
    req = urllib.request.Request(MTOP_URL, data=json.dumps(body).encode(),
                                 headers=MTOP_HEADERS)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def fetch_mobile(pid: str) -> dict:
    """返回 {field: (value, Provenance)}"""
    d = _mtop(pid)
    if d.get("code") != 0:
        return {}
    gid = ((d.get("data") or {}).get("product") or {}).get("defaultGid")
    if gid:
        d2 = _mtop(pid, gid)
        if d2.get("code") == 0:
            d = d2
    data = d.get("data") or {}
    prod = data.get("product") or {}
    gl = (data.get("goodsInfo") or {}).get("goodsList") or []
    g = gl[0] if gl else {}
    params = {i.get("name"): i.get("value")
              for i in (g.get("classParameters") or {}).get("list") or []}
    attrs: dict[str, list] = {}
    for a in ((data.get("saleAttributeInfo") or {}).get("saleAttributeList") or []):
        attrs[a.get("attributeName")] = [v.get("attributeValueName")
                                         for v in a.get("attributeValueList") or []]
    bs = data.get("buyerShow") or {}
    ask = data.get("askAll") or {}
    detail_url = f"https://m.mi.com/commodity/detail/{pid}"

    def P(page: str, path: str, ui: str = "") -> Provenance:
        return Provenance(source=SRC_M, site="m.mi.com", page=page,
                          ui_location=ui, api="POST /mtop/xiaomishop/product/info",
                          json_path=path, url=detail_url,
                          raw_field=path.split(".")[-1])

    out: dict[str, tuple] = {}
    out["name"] = ((prod.get("name") or "").strip(), P("移动端商品详情页标题", "data.product.name", "商品名"))
    out["short_title"] = (prod.get("shortTitle"), P("移动端商品详情页副标题", "data.product.shortTitle", "副标题"))
    out["sell_points"] = (prod.get("sellPointList") or [],
                          P("移动端商品详情页卖点条", "data.product.sellPointList[]", "卖点"))
    out["gid"] = (prod.get("defaultGid"), P("接口字段", "data.product.defaultGid"))
    out["commodity_id"] = (g.get("commodityId"), P("接口字段", "data.goodsInfo.goodsList[0].commodityId"))
    out["goods_id"] = (g.get("goodsId"), P("接口字段", "data.goodsInfo.goodsList[0].goodsId"))
    out["sku"] = (g.get("sku"), P("接口字段", "data.goodsInfo.goodsList[0].sku"))
    out["price"] = (g.get("price"), P("移动端商品详情页价格区", "data.goodsInfo.goodsList[0].price", "现价"))
    out["market_price"] = (g.get("marketPrice"),
                           P("移动端商品详情页划线价", "data.goodsInfo.goodsList[0].marketPrice", "划线价"))
    out["img_url"] = (g.get("imgUrl"), P("商品主图", "data.goodsInfo.goodsList[0].imgUrl"))
    out["carousel"] = ([c.get("imgUrl") for c in (g.get("carouselList") or []) if c.get("imgUrl")],
                       P("移动端商品详情页商品图轮播", "data.goodsInfo.goodsList[0].carouselList[].imgUrl", "轮播图"))
    out["colors"] = (attrs.get("颜色", []),
                     P("移动端商品详情页颜色选择器",
                       "data.saleAttributeInfo.saleAttributeList[name=颜色]", "可选颜色"))
    out["attrs"] = (attrs, P("销售属性", "data.saleAttributeInfo.saleAttributeList[]"))
    out["evaluate_total"] = (bs.get("total"), P("移动端商品详情页评论数", "data.buyerShow.total", "评论数"))
    out["evaluate_real"] = (bs.get("realTotal"), P("移动端商品详情页评论数", "data.buyerShow.realTotal", "评论数"))
    out["review_tags"] = (bs.get("tags") or [], P("移动端商品详情页评价标签", "data.buyerShow.tags[]", "大家评价"))
    out["buyer_imgs"] = ((bs.get("imgs") or [])[:12],
                         P("移动端商品详情页买家秀", "data.buyerShow.imgs[]", "买家秀"))
    out["qa_total"] = (ask.get("total"), P("移动端商品详情页问答总数", "data.askAll.total", "问大家"))
    out["qa_items"] = (ask.get("items") or [], P("移动端商品详情页问答列表", "data.askAll.items[]", "问大家"))
    # 关键参数整块（由 normalize 展开到顶层）
    out["params"] = (params, P("移动端商品详情页「关键参数」表",
                               "data.goodsInfo.goodsList[0].classParameters.list[]", "关键参数"))
    return out


# ---------------- PC ----------------

def fetch_pc(pid: str) -> dict:
    try:
        d = json.loads(_get(f"{VIEW_URL}?product_id={pid}&version=2"))
    except Exception:
        return {}
    if d.get("code") != 200:
        return {}
    pv = d.get("data") or {}
    pi = pv.get("product_info") or {}
    gl = pv.get("goods_list") or []
    gi = (gl[0] or {}).get("goods_info", {}) if gl else {}
    tabs, imgs = [], []
    for tab in ((pv.get("extend_info") or {}).get("desc_tabs_view") or []):
        tabs.append(tab.get("name"))
        for c in (tab.get("tab_content") or []):
            p = c.get("plain_view") or {}
            if p.get("img"):
                imgs.append({"tab": tab.get("name"), "img": p["img"],
                             "w": p.get("w"), "h": p.get("h")})
    url = f"https://www.mi.com/shop/buy/detail?product_id={pid}"
    api = "GET api2.order.mi.com/product/view?product_id=X&version=2"

    def P(page: str, path: str, ui: str = "") -> Provenance:
        return Provenance(source=SRC_P, site="www.mi.com", page=page, ui_location=ui,
                          api=api, json_path=path, url=url, raw_field=path.split(".")[-1])

    out = {}
    if pi.get("product_desc"):
        out["desc"] = (pi.get("product_desc"), P("PC 商品页商品简介", "data.product_info.product_desc", "商品简介"))
    if gi.get("price"):
        out["pc_price"] = (gi.get("price"), P("PC 商品页价格", "data.goods_list[0].goods_info.price", "现价"))
    out["buy_options"] = (pv.get("buy_option") or [],
                          P("PC 商品页规格选择器", "data.buy_option[]", "选择规格"))
    out["pc_tabs"] = (tabs, P("PC 商品页图文页签", "data.extend_info.desc_tabs_view[].name", "商品详情"))
    out["pc_imgs"] = (imgs, P("PC 商品页「商品详情」图文页签",
                              "data.extend_info.desc_tabs_view[].tab_content[].plain_view", "商品详情"))
    return out
