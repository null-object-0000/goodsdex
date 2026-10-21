"""Apple 官方文稿历史目录；文档级机型参考，不推断国行 SKU 或停售状态。"""

from __future__ import annotations

import gzip
import hashlib
import html
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from ..facts import Capture, CaptureStatus, Assertion
from .apple_cn import text

SOURCE = "apple_support"
VERSION = "apple-support-v1"
ORIGIN = "https://support.apple.com"
IDENTIFY = {"iphone": "108044", "ipad": "108043"}
NAME_PATTERNS = {
    "iphone": r"^iPhone",
    "ipad": r"^iPad",
    "mac": r"^(?:Mac|iMac|eMac|PowerBook|Power Mac|Power Macintosh|iBook|Xserve)",
    "watch": r"^Apple Watch",
    "airpods": r"^AirPods",
    "homepod": r"^HomePod",
    "vision": r"^Apple Vision",
    "displays": r"(?:Display|显示器)",
    "airtag": r"^AirTag",
}
FAMILIES = {
    "iphone": ("iphone", "手机"),
    "ipad": ("ipad", "平板"),
    "mac": ("mac", "电脑"),
    "watch": ("watch", "手表"),
    "airpods": ("airpods", "耳机"),
    "homepod": ("homepod", "音箱"),
    "vision": ("vision", "空间计算设备"),
    "displays": ("displays", "显示器"),
    "airtag": ("accessories", "配件"),
}


def official_url(url, base=ORIGIN):
    p = urllib.parse.urlsplit(urllib.parse.urljoin(base, html.unescape(url)))
    if (
        p.scheme != "https"
        or p.hostname != "support.apple.com"
        or p.port
        or p.username
        or p.password
    ):
        raise ValueError("只接受 Apple Support 官方 HTTPS 链接")
    legacy = bool(re.fullmatch(r"/kb/(?:SP|HT)\d+", p.path))
    if not legacy and not re.match(r"/[a-z]{2}-[a-z]{2}/", p.path):
        raise ValueError("支持文稿必须带实际地区路径")
    query = urllib.parse.parse_qs(p.query)
    locale = query.get("locale", [""])[0]
    query = (
        urllib.parse.urlencode({"locale": locale})
        if legacy and re.fullmatch(r"[a-z]{2}_[A-Z]{2}", locale)
        else ""
    )
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path.rstrip("/"), query, ""))


class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        official_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, timeout=25):
    url = official_url(url)
    cap = Capture.make(SOURCE, url, parser_version=VERSION)
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "GoodsDex/1.0 (official product documentation)"}
        )
        with urllib.request.build_opener(Redirect()).open(
            req, timeout=timeout
        ) as response:
            cap.url = official_url(response.url)
            cap.http_status = response.status
            body = response.read()
            if body.startswith(b"\x1f\x8b"):
                body = gzip.decompress(body)
            cap.response_raw = body.decode("utf-8")
            # Capture.make must hash the actual response, not the initial empty value.
            hashed = Capture.make(
                SOURCE, cap.url, cap.response_raw, parser_version=VERSION
            )
            hashed.http_status = cap.http_status
            return hashed
    except urllib.error.HTTPError as exc:
        cap.http_status = exc.code
        cap.status = (
            CaptureStatus.RATE_LIMITED
            if exc.code == 429
            else CaptureStatus.NOT_FOUND
            if exc.code == 404
            else CaptureStatus.SOURCE_ERROR
        )
        cap.error = str(exc)
    except (OSError, ValueError, UnicodeError) as exc:
        cap.status = CaptureStatus.TRANSPORT_ERROR
        cap.error = str(exc)
    return cap


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            a = dict(attrs)
            self.current = [a.get("href", ""), "", a]

    def handle_data(self, data):
        if self.current is not None:
            self.current[1] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append(self.current)
            self.current = None


def links(body, base):
    parser = Anchors()
    parser.feed(body)
    result = []
    for href, label, attrs in parser.links:
        try:
            url = official_url(href, base)
        except ValueError:
            continue
        result.append((url, text(label), attrs))
    return result


def model_links(body, base, family):
    """只跟随目录真实产品卡；pl 分组页（如 Watch Series）继续展开。"""
    slug = FAMILIES[family][0]
    result = {}
    for url, label, attrs in links(body, base):
        if re.fullmatch(
            r"/[a-z]{2}-[a-z]{2}/docs/" + slug + r"/(?:pl)?\d+",
            urllib.parse.urlsplit(url).path,
        ):
            name = attrs.get("data-ss-analytics-link-text") or label
            if (
                name
                and re.search(NAME_PATTERNS[family], name, re.I)
                and not re.search(
                    r"电池|充电线|键盘|Pencil|Keyboard|Battery",
                    name,
                    re.I,
                )
            ):
                if re.search(r"充电盒|Charging Case", name, re.I) and not re.search(
                    r"配|with", name, re.I
                ):
                    continue
                result[url] = name
    return result


def specs_links(body, base):
    return sorted(
        {
            url
            for url, label, attrs in links(body, base)
            if re.search(
                r"技术规格|tech(?:nical)? specs|technical specifications",
                label + " " + attrs.get("data-ss-analytics-link-text", ""),
                re.I,
            )
            and re.fullmatch(
                r"(?:/[a-z]{2}-[a-z]{2}/(?:\d+|[A-Z]{2}\d+)|/kb/(?:SP|HT)\d+)",
                urllib.parse.urlsplit(url).path,
            )
        }
    )


class Article(HTMLParser):
    """保留正文标题层级、段落/列表行和脚注，不混入导航或执行脚本。"""

    def __init__(self):
        super().__init__()
        self.active = False
        self.done = False
        self.heading = None
        self.title = ""
        self.sections = []
        self.current = None
        self.line = []
        self.ignore = 0
        self.image = None

    def flush(self):
        value = text("".join(self.line))
        self.line = []
        if value:
            if self.current is None:
                self.current = {"heading": "概览", "level": 1, "lines": []}
                self.sections.append(self.current)
            self.current["lines"].append(value)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img" and "gb-image" in a.get("class", "").split() and not self.image:
            image = a.get("src", "")
            if image.startswith("https://cdsassets.apple.com/"):
                self.image = image
        if tag == "h1" and not self.done:
            self.active = True
        if not self.active or self.done:
            return
        if a.get("id") in ("ac-gf-label", "helpful-rating-wrapper") or tag == "footer":
            self.flush()
            self.done = True
            return
        if tag in ("script", "style", "noscript"):
            self.ignore += 1
        if self.ignore:
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.flush()
            self.heading = [tag, []]
        elif tag in ("p", "li", "br", "tr", "td", "div"):
            self.flush()
        if tag == "img" and not self.image:
            image = a.get("src", "")
            if image.startswith("https://cdsassets.apple.com/"):
                self.image = image

    def handle_data(self, data):
        if not self.active or self.done or self.ignore:
            return
        if self.heading:
            self.heading[1].append(data)
        else:
            self.line.append(data)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.ignore:
            self.ignore -= 1
            return
        if not self.active or self.done or self.ignore:
            return
        if self.heading and tag == self.heading[0]:
            value = text("".join(self.heading[1]))
            if tag == "h1":
                self.title = value
            else:
                self.current = {"heading": value, "level": int(tag[1]), "lines": []}
                self.sections.append(self.current)
            self.heading = None
        elif tag in ("p", "li", "tr", "td", "div"):
            self.flush()


def _assert(cap, subject, attribute, value, **kwargs):
    key = f"{cap.capture_id}|{subject}|{attribute}"
    return Assertion(
        hashlib.sha256(key.encode()).hexdigest()[:16],
        subject,
        cap.capture_id,
        SOURCE,
        attribute,
        value,
        parser_version=VERSION,
        **kwargs,
    )


def parse_specs(cap, family, docs_url):
    parser = Article()
    parser.feed(cap.response_raw)
    parser.flush()
    title = parser.title
    # Two official Mac Pro 2019 specification documents use a language suffix.
    legacy_specs = (
        re.search(r" - 简体中文$", title)
        and len(
            {s["heading"] for s in parser.sections}
            & {"处理器", "内存", "图形处理器", "存储设备"}
        )
        >= 3
    )
    if (
        not re.search(r"技术规格|Technical Specifications|Tech Specs", title, re.I)
        and not legacy_specs
    ):
        raise ValueError("链接未返回技术规格正文")
    name = re.sub(
        r"\s*[-–—:：]\s*(?:技术规格|Technical Specifications|Tech Specs|简体中文)\s*$",
        "",
        title,
        flags=re.I,
    ).strip()
    sections = [s for s in parser.sections if s["lines"]]
    if not sections:
        raise ValueError("技术规格正文为空")
    doc_id = urllib.parse.urlsplit(cap.url).path.rsplit("/", 1)[-1]
    subject = f"GLOBAL:apple_support:model:{doc_id}"
    values = {"name": name, "price": None, "specs_sections": sections}
    assertions = []
    if parser.image:
        values["img_url"] = parser.image
        assertions.append(
            _assert(
                cap, subject, "img_url", parser.image, locator="html:img.gb-image@src"
            ).to_dict()
        )
    for attribute, value, locator in [
        ("name", title, "html:h1"),
        (
            "specs_sections",
            sections,
            "html:article headings and paragraph/list lines after h1",
        ),
    ]:
        assertion = _assert(
            cap,
            subject,
            attribute,
            value,
            locator=locator,
            qualifiers={"scope": "model_document", "locale": cap.url.split("/")[3]},
        )
        if attribute == "name":
            assertion.normalized_value = name
            assertion.normalization_rule_version = VERSION
        assertions.append(assertion.to_dict())
    # Only an explicit introduction/year statement or year in model title; never article update date.
    overview = (
        " ".join(sections[0]["lines"]) if sections[0]["heading"] == "概览" else ""
    )
    year = re.search(
        r"(?:推出年份|Year introduced)\s*[：:]\s*((?:19|20)\d{2})", overview, re.I
    )
    if not year:
        year = re.search(r"\b((?:19|20)\d{2})\b", name)
    if year:
        values["model_year"] = int(year[1])
        a = _assert(
            cap,
            subject,
            "model_year",
            year[0],
            locator="html:h1 or introductory paragraph",
            qualifiers={"precision": "year"},
        )
        a.normalized_value = int(year[1])
        a.normalization_rule_version = VERSION
        assertions.append(a.to_dict())
    return {
        "product": {
            "product_id": subject,
            "name": name,
            "source": SOURCE,
            "brand": "Apple",
            "market": "GLOBAL",
            "family": family,
            "category": FAMILIES[family][1],
            "kind": "accessory" if family == "airtag" else "machine",
            "record_level": "model_reference",
            "catalog_scope": "historical_and_current",
            "sale_status": "unverified",
            "price_status": "not_collected",
            "price_kind": "not_applicable",
            "source_url": cap.url,
            "source_docs_url": docs_url,
            "document_locale": cap.url.split("/")[3],
        },
        "fetched_at": cap.fetched_at,
        "parser_version": VERSION,
        "view": {
            "values": values,
            "selected_from": {a["attribute"]: a["assertion_id"] for a in assertions},
        },
        "assertions": assertions,
        "captures": [cap.to_dict()],
    }
