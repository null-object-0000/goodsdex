"""HTML 解析工具：标签配对 + JS 注入噪声清洗。

实战教训（ZOL）：
参数其实在 raw HTML 里，但页面 JS 注入了「纠错」「问豆包」按钮，
污染了 th/td 结构，导致解析出「产品型号 = 问豆包」。
所以标签配对后必须清洗尾部注入。
"""
from __future__ import annotations
import html as H
import re

# 常见的 JS 注入噪声（出现在值尾部的按钮/标记）
NOISE_TAIL = r"(纠错|问豆包|查看外观>?|更多.{0,14}手机>?|复制表格|加入对比栏|举报|反馈)"


def strip_noise(v: str) -> str:
    """剔除值尾部的 JS 注入噪声"""
    if not isinstance(v, str):
        return v
    s = v
    for _ in range(3):
        s = re.sub(rf"\s*{NOISE_TAIL}\s*$", "", s)
    # 站点导航后缀（如 "6 公司简介|公司历程|..."）
    s = re.sub(r"\s+\S*\s*(公司简介|公司历程|营销推广|媒体合作|品牌大全)\s*\|.*$", "", s)
    return s.strip()


def clean_tag(s: str) -> str:
    s = H.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).strip()


def pairs_from_html(html_str: str) -> dict[str, str]:
    """<th>键</th><td>值</td> 配对（ZOL 等参数页通用）"""
    rows = re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", html_str, re.S)
    out = {}
    for k, v in rows:
        k2, v2 = strip_noise(clean_tag(k)), strip_noise(clean_tag(v))
        if k2 and v2 and k2 not in out:
            out[k2] = v2
    return out


def pairs_from_dl(html_str: str) -> dict[str, str]:
    """<dt>键</dt><dd>值</dd> 配对"""
    rows = re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", html_str, re.S)
    return {strip_noise(clean_tag(k)): strip_noise(clean_tag(v))
            for k, v in rows if strip_noise(clean_tag(k))}


def visible_text(html_str: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_str or "", flags=re.S | re.I)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", t)))


def pairs_from_text(text: str) -> dict[str, str]:
    """可见文本里的「键 值」行（备选，噪声较多）"""
    out, cur = {}, None
    for line in (text or "").split("\n"):
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^(\S{2,20})[\t\u3000 ]{1,}(\S.{0,80})$", s)
        if m and not re.match(r"^[\d\W]+$", m.group(1)):
            out[m.group(1)] = strip_noise(m.group(2))
            cur = m.group(1)
        elif cur and cur in out:
            out[cur] = (out[cur] + " " + s).strip()[:120]
    return out


def extract_images(html_str: str, host_hint: str = "") -> list[str]:
    """页面里的图片直链"""
    urls = re.findall(r'(?:data-src|src|data-original)="((?:https?:)?//[^"]+\.(?:png|jpg|jpeg|webp))"',
                      html_str or "", re.I)
    out, seen = [], set()
    for u in urls:
        u = ("https:" + u) if u.startswith("//") else u
        if host_hint and host_hint not in u:
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
