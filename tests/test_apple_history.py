import json

import pytest

from goodsdex.apple import publish_apple
from goodsdex.apple_history import crawl_history
from goodsdex.facts import Capture, CaptureStatus
from goodsdex.publish import to_public
from goodsdex.sources import apple_support as support

SEED = "https://support.apple.com/zh-cn/docs/iphone"
DOC = SEED + "/100"
SPEC = "https://support.apple.com/zh-cn/100001"
BODY = """<header>忽略导航</header><h1>iPhone Test - 技术规格</h1>
<p>推出年份：2017 年</p><h3>容量</h3><ul><li>64GB</li><li>256GB</li></ul>
<h3>蜂窝网络</h3><p>A1111（美国）；A2222（中国大陆）</p>
<p>支持条件：取决于运营商</p><div id="helpful-rating-wrapper">有帮助？</div>"""


def cap(body=BODY, url=SPEC, status=CaptureStatus.SUCCESS):
    return Capture.make(
        support.SOURCE, url, body, status=status, parser_version=support.VERSION
    )


def test_model_not_sku_and_regional_conditions_kept():
    rec = support.parse_specs(cap(), "iphone", DOC)
    item = to_public(rec)
    assert item["id"] == "GLOBAL:apple_support:model:100001"
    assert item["record_level"] == "model_reference"
    assert item["market"] == "GLOBAL" and item["sale_status"] == "unverified"
    assert item["price"] is None and item["variant_id"] is None
    assert item["params"]["model_year"] == 2017
    sections = item["params"]["specs_sections"]
    assert sections[1]["lines"] == ["64GB", "256GB"]
    assert "A2222（中国大陆）" in sections[2]["lines"][0]
    assert sections[2]["lines"][1] == "支持条件：取决于运营商"
    assert "有帮助" not in json.dumps(sections, ensure_ascii=False)
    assert all(
        a["capture_id"] == rec["captures"][0]["capture_id"] for a in rec["assertions"]
    )


def test_article_update_year_never_becomes_model_year():
    rec = support.parse_specs(
        cap(BODY.replace("推出年份：2017 年", "发布日期：2026 年")), "iphone", DOC
    )
    assert "model_year" not in rec["view"]["values"]
    assert not any(a["attribute"] == "price" for a in rec["assertions"])


def test_year_from_model_title_and_locale_explicit():
    rec = support.parse_specs(
        cap(
            BODY.replace("iPhone Test", "Mac mini (2014)").replace(
                "推出年份：2017 年", ""
            ),
            "https://support.apple.com/en-us/100001",
        ),
        "mac",
        DOC,
    )
    assert rec["view"]["values"]["model_year"] == 2014
    assert rec["product"]["document_locale"] == "en-us"
    assert rec["product"]["market"] == "GLOBAL"


def test_support_host_and_real_legacy_locale_links():
    for url in [
        "http://support.apple.com/zh-cn/1",
        "https://support.apple.com.evil/zh-cn/1",
        "https://support.apple.com:443/zh-cn/1",
        "https://user@support.apple.com/zh-cn/1",
        "https://evil.test/zh-cn/1",
    ]:
        with pytest.raises(ValueError):
            support.official_url(url)
    html = '<a href="https://support.apple.com/kb/SP770?locale&#x3D;zh_CN">iPhone X 的技术规格</a>'
    assert support.specs_links(html, DOC) == [
        "https://support.apple.com/kb/SP770?locale=zh_CN"
    ]


def test_product_cards_exclude_cross_family_accessories_and_dedupe():
    body = f'<a href="{DOC}">iPhone Test</a><a href="{DOC}">iPhone Test</a><a href="{SEED}/200">AirPods Pro</a><a href="{SEED}/300">iPhone MagSafe 电池</a>'
    assert support.model_links(body, SEED, "iphone") == {DOC: "iPhone Test"}
    assert support.model_links(
        '<a href="/zh-cn/docs/watch/pl213">Apple Watch Series 10</a>', SEED, "watch"
    )


def test_reject_non_specs_or_empty_document():
    for body in ["<h1>支持首页</h1><p>无规格</p>", "<h1>iPhone - 技术规格</h1>"]:
        with pytest.raises(ValueError):
            support.parse_specs(cap(body), "iphone", DOC)


def transport(url):
    pages = {
        SEED: f'<a href="{DOC}">iPhone Test</a>',
        DOC: f'<a href="{SPEC}">技术规格</a>',
        "https://support.apple.com/zh-cn/108044": f'<a href="{SPEC}">iPhone Test 技术规格</a>',
        SPEC: BODY,
    }
    return cap(pages[url], url)


def test_cache_failure_preserves_records_evidence_times_and_null_prices(tmp_path):
    out, raw = tmp_path / "cats", tmp_path / "raw"
    report = crawl_history(out, raw, ["iphone"], transport=transport)
    assert report["models"] == 1 and not report["errors"]
    path = out / "Apple_history_iphone.json"
    previous = path.read_bytes()
    record = json.loads(previous)[0]
    assert all(c["raw_ref"] for c in record["captures"])
    calls = []

    def cached(url):
        calls.append(url)
        assert url != DOC and url != SPEC
        return transport(url)

    report = crawl_history(out, raw, ["iphone"], transport=cached)
    assert report["cached"] >= 1 and path.read_bytes() == previous

    def failed(url):
        return cap("", url, CaptureStatus.TRANSPORT_ERROR)

    report = crawl_history(out, raw, ["iphone"], transport=failed, max_age_days=0)
    assert report["errors"] and path.read_bytes() == previous
    assert json.loads(path.read_text())[0]["fetched_at"] == record["fetched_at"]


def test_incremental_publish_keeps_current_and_xiaomi_no_historical_prices(tmp_path):
    cats, public = tmp_path / "cats", tmp_path / "public"
    cats.mkdir()
    public.mkdir()
    rec = support.parse_specs(cap(), "iphone", DOC)
    (cats / "Apple_history_iphone.json").write_text(json.dumps([rec]))
    original = [
        {"id": "xiaomi:1", "price": 100, "name": "小米"},
        {
            "id": "CN:apple_cn:commodity:TESTCH/A",
            "source": "apple_cn",
            "price": 999,
            "price_fetched_at": "2026-10-01T00:00:00+08:00",
        },
    ]
    (public / "goods.json").write_text(json.dumps(original))
    publish_apple(cats, public)
    publish_apple(cats, public)
    merged = json.loads((public / "goods.json").read_text())
    assert len(merged) == 3
    assert all(x in merged for x in original)
    prices = json.loads((public / "prices/apple/latest.json").read_text())["prices"]
    assert list(prices) == ["CN:apple_cn:commodity:TESTCH/A"]
    assert next(x for x in merged if x["source"] == "apple_support")["price"] is None


def test_historical_official_product_image_and_options_remain_model_scoped():
    body = (
        '<img class="gb-image" src="https://cdsassets.apple.com/iphone-test.png">'
        + BODY
    )
    item = to_public(support.parse_specs(cap(body), "iphone", DOC))
    assert item["image_url"] == "https://cdsassets.apple.com/iphone-test.png"
    assert item["record_level"] == "model_reference" and item["variant_attrs"] is None


def test_duplicate_spec_links_resolve_to_one_document(tmp_path):
    other = "https://support.apple.com/en-us/100001"

    def duplicate(url):
        if url == DOC:
            return cap(
                f'<a href="{SPEC}">技术规格</a><a href="{other}">Tech Specs</a>', url
            )
        if url == other:
            # Real redirect target, not a fabricated extra model.
            return cap(BODY, SPEC)
        return transport(url)

    report = crawl_history(
        tmp_path / "cats", tmp_path / "raw", ["iphone"], transport=duplicate
    )
    assert report["models"] == 1 and not report["errors"]
    rec = json.loads((tmp_path / "cats/Apple_history_iphone.json").read_text())[0]
    assert set(rec["product"]["spec_request_urls"]) == {SPEC, other}

    def cached(url):
        assert url not in (SPEC, other, DOC)
        return transport(url)

    again = crawl_history(
        tmp_path / "cats", tmp_path / "raw", ["iphone"], transport=cached
    )
    assert again["models"] == 1 and not again["errors"]


def test_airpods_with_charging_case_is_a_model_not_case_accessory():
    base = "https://support.apple.com/zh-cn/docs/airpods"
    body = f'<a href="{base}/1">AirPods Pro 2（配 MagSafe 充电盒）</a><a href="{base}/2">AirPods 无线充电盒</a>'
    assert support.model_links(body, base, "airpods") == {
        base + "/1": "AirPods Pro 2（配 MagSafe 充电盒）"
    }


def test_legacy_mac_specs_language_title_requires_real_spec_sections():
    body = "<h1>Mac Pro (2019) - 简体中文</h1><h3>处理器</h3><p>Xeon</p><h3>内存</h3><p>32 GB</p><h3>图形处理器</h3><p>Radeon</p>"
    rec = support.parse_specs(cap(body), "mac", DOC)
    assert rec["product"]["name"] == "Mac Pro (2019)"
    with pytest.raises(ValueError):
        support.parse_specs(
            cap("<h1>Mac Pro - 简体中文</h1><p>其他文档</p>"), "mac", DOC
        )


@pytest.mark.parametrize('name', [
    'macOS Big Sur', 'macOS Sierra', 'Mac OS X v10.6 Snow Leopard',
    'Mac OS X v10.5 Leopard', 'iOS 18', 'iPadOS 18',
])
def test_software_titles_never_become_models(name):
    assert support.is_software_title(name)
    with pytest.raises(support.SoftwarePage):
        support.parse_specs(cap(BODY.replace('iPhone Test', name)), 'mac', DOC)
    base = 'https://support.apple.com/zh-cn/docs/mac'
    assert support.model_links(f'<a href="{base}/1">{name}</a>', base, 'mac') == {}


def test_real_macbook_model_survives_software_filter():
    name = 'MacBook Pro (14-inch, 2021)'
    assert not support.is_software_title(name)
    rec = support.parse_specs(cap(BODY.replace('iPhone Test', name)), 'mac', DOC)
    assert rec['product']['name'] == name
    base = 'https://support.apple.com/zh-cn/docs/mac'
    assert support.model_links(f'<a href="{base}/1">{name}</a>', base, 'mac') == {base + '/1': name}


def test_cached_software_not_restored_on_failed_crawl(tmp_path):
    out = tmp_path / 'cats'
    out.mkdir()
    path = out / 'Apple_history_mac.json'
    rec = support.parse_specs(cap(BODY.replace('iPhone Test', 'MacBook Pro (14-inch, 2021)')), 'mac', DOC)
    software = json.loads(json.dumps(rec))
    software['product']['name'] = 'macOS Big Sur'
    software['product']['product_id'] = 'GLOBAL:apple_support:model:111980'
    path.write_text(json.dumps([rec, software]))
    report = crawl_history(out, tmp_path / 'raw', ['mac'], transport=lambda url: cap('', url, CaptureStatus.TRANSPORT_ERROR))
    assert json.loads(path.read_text()) == [rec]
    assert len(report['filtered_software']) == 1


def test_software_specs_reached_through_model_link_are_reported_as_filtered(tmp_path):
    seed = 'https://support.apple.com/zh-cn/docs/mac'
    model = seed + '/1'
    def redirected_software(url):
        pages = {
            seed: f'<a href="{model}">MacBook Pro (14-inch, 2021)</a>',
            model: f'<a href="{SPEC}">技术规格</a>',
            SPEC: BODY.replace('iPhone Test', 'macOS Big Sur'),
        }
        return cap(pages[url], url)
    report = crawl_history(tmp_path / 'cats', tmp_path / 'raw', ['mac'], transport=redirected_software)
    assert report['models'] == 0 and report['errors'] == []
    assert len(report['filtered_software']) == 1
