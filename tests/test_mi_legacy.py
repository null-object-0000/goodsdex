import json
import pytest
from goodsdex.mi_legacy import page_info, script_links, specs, official_url, crawl
from goodsdex.facts import Capture
from goodsdex.publish import to_public

PAGE = 'var $GLOBAL_PAGE_INFO = {"product_info":{"product_id":"19963","name":"Redmi 显示器 G27Q 2025款"}};<script src="//cdn.cnbj1.fds.api.mi-img.com/mi.com-assets/shop/pro/js/product/redmi-monitors/g27q-2025/index.abc.js"></script>'
JS = (
    'specsArray:[{name:"产品型号",specs:"P27QCA-RG"},{name:"最大刷新率",specs:"180Hz"}]'
)
URL = "https://www.mi.com/redmi-monitors/g27q-2025"


def test_official_legacy_identity_and_link_evidence_not_guessed():
    assert page_info(PAGE)["product_id"] == "19963"
    assert len(script_links(PAGE)) == 1
    assert specs(JS)[0][:2] == ("产品型号", "P27QCA-RG")
    for url in [
        "https://www.mi.com.evil/a",
        "http://www.mi.com/a",
        "https://user@www.mi.com/a",
    ]:
        with pytest.raises(ValueError):
            official_url(url)
    with pytest.raises(ValueError):
        page_info("<h1>没有产品编号</h1>")


def test_old_model_no_quote_and_failed_refresh_keeps_previous(tmp_path):
    def fetch(url):
        return Capture.make("mi_cn_legacy", url, JS if url.endswith(".js") else PAGE)

    def collect(*args, **kwargs):
        return {
            "product": {
                "product_id": "CN:mi_cn:product:19963",
                "kind": "machine",
                "category": "显示器",
            },
            "fetched_at": "2026-10-22T00:00:00+08:00",
            "captures": [
                Capture.make(
                    "mi_cn_pc", "https://api2.order.mi.com/product/view", "{}"
                ).to_dict()
            ],
            "assertions": [],
            "view": {
                "values": {"price": 1299, "pc_price": "1299", "gid": 2230001683},
                "selected_from": {},
            },
        }

    out = tmp_path / "cats"
    raw = tmp_path / "raw"
    report = crawl(
        out, raw, [{"url": URL, "category": "显示器"}], fetch, collect, pause=0
    )
    assert not report["errors"]
    record = json.loads((out / "Mi_legacy.json").read_text())[0]
    item = to_public(record)
    assert item["model"] == "P27QCA-RG" and item["lookup_keys"] == ["P27QCA-RG"]
    assert item["price"] is None and item["market_price"] is None
    assert item["params"]["最大刷新率"] == "180Hz"
    assert (
        item["record_level"] == "model_reference"
        and item["sale_status"] == "unverified"
    )
    old = (out / "Mi_legacy.json").read_bytes()

    def fail(url):
        raise OSError("unavailable")

    assert crawl(
        out, raw, [{"url": URL, "category": "显示器"}], fail, collect, pause=0
    )["errors"]
    assert (out / "Mi_legacy.json").read_bytes() == old


def test_manual_component_separate_from_robot_and_version_checked(tmp_path):
    import hashlib
    from goodsdex.mi_legacy import manual_component

    data = b"%PDF-test"
    seed = {
        "url": "https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/test.pdf",
        "sha256": hashlib.sha256(data).hexdigest(),
        "model": "JZ2301",
        "name": "米家全能基座 JZ2301",
        "category": "扫拖基座",
        "pdf_page": 14,
        "printed_page": 23,
        "reviewed_at": "2026-10-22",
        "facts": {"型号": "JZ2301", "产品类型": "全能基座（非扫地机器人主机）"},
    }
    item = to_public(manual_component(seed, tmp_path, read=lambda u: data))
    assert item["id"] == "CN:mi_cn:reference:JZ2301"
    assert (
        item["kind"] == "accessory"
        and item["model"] == "JZ2301"
        and item["price"] is None
    )
    with pytest.raises(ValueError, match="版本变化"):
        manual_component(seed, tmp_path, read=lambda u: b"changed")
