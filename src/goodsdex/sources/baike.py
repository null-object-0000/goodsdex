"""百度百科源：精确发布时间、代际定位。

严格匹配原则：词条名必须与商品名完全一致（归一化后），否则视为未找到。
模糊匹配曾把「REDMI Buds 8 青春版」匹配到「REDMI Buds 8 Pro」——
这种错误比没有数据更危险。

注意：百科对 curl 返回 403，必须用无头浏览器取内容。
"""
from __future__ import annotations
import re
import urllib.parse

from ..model import Provenance
from ..parse import html as ph

SRC = "baike"
MIN_MATCH = "exact"


def _norm(s: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", (s or "").lower())


def find_lemma_url(name: str) -> str | None:
    """找百科词条 — 词条名必须与商品名完全一致（归一化后）"""
    from hermes_tools import web_search
    cands = []
    for q in [f'"{name}" 百度百科 site:baike.baidu.com', f"{name} 百度百科"]:
        r = web_search(q, limit=6)
        for h in (r.get("data", {}).get("web", []) or []):
            if "baike.baidu.com/item" in h.get("url", ""):
                cands.append(h["url"])
    target = _norm(name)
    for u in dict.fromkeys(cands):
        slug = urllib.parse.unquote(u.split("/item/")[-1].split("/")[0]).split("#")[0]
        if _norm(slug) == target:
            return u
    return None


def parse(html_str: str, text: str = "") -> dict:
    t = ph.visible_text(html_str) or re.sub(r"\s+", " ", text or "")
    info = {}
    for k in ["中文名", "发布时间", "上市时间", "发行时间", "所属公司", "产品类型",
              "所属品牌", "产品型号"]:
        m = re.search(rf"{k}\s*([^\s]{{2,30}})", t)
        if m:
            info[k] = m.group(1)[:30]
    rel = ""
    m = re.search(r"(?:于)?\s*(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日\s*(?:正式)?\s*"
                  r"(?:发布|上市|开售|推出)", t)
    if not m:
        m = re.search(r"(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日", t)
    if m:
        rel = f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    dates = [f"{a}-{b.zfill(2)}-{c.zfill(2)}"
             for a, b, c in re.findall(r"(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日", t)]
    gen = []
    for pat in [r"是([^\s，。]{2,24}?)的继任", r"继([^\s，。]{2,24}?)之后",
                r"([^\s，。]{2,20}?)的升级版", r"首款([^\s，。]{2,20})", r"取代([^\s，。]{2,20})"]:
        gen += [m2.group(1) for m2 in re.finditer(pat, t)]
    return {"infobox": info, "release_date": rel,
            "all_dates": list(dict.fromkeys(dates))[:6],
            "gen_hints": list(dict.fromkeys(gen))[:4], "chars": len(t)}


def fetch(name: str, html_str: str = "", text: str = "", url: str = "") -> dict:
    """采集一个商品的百科数据。html_str/text 由调用方用无头浏览器取好传入"""
    if not url:
        url = find_lemma_url(name)
        if not url:
            return {}
    r = parse(html_str, text)

    def P(page: str, path: str, ui: str = "") -> Provenance:
        return Provenance(source=SRC, site="baike.baidu.com", page=page, ui_location=ui,
                          api="无头浏览器渲染", json_path=path, url=url, raw_field=path)

    out = {}
    if r["release_date"]:
        out["发布日期"] = (r["release_date"], P("百科词条信息框「发布时间」", "release_date", "发布时间"))
    if r["infobox"].get("产品类型"):
        out["形态"] = (r["infobox"]["产品类型"], P("百科词条信息框「产品类型」", "infobox.产品类型", "产品类型"))
    if r["gen_hints"]:
        out["代际线索"] = (r["gen_hints"], P("百科词条正文", "gen_hints", "正文"))
    return out
