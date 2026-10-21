"""Apple adapter boundary tests, deterministic captured-shaped fixtures (no network)."""

import json
from pathlib import Path

from goodsdex.sources import apple_cn as apple
from goodsdex.facts import Capture, CaptureStatus
from goodsdex.apple import crawl, publish_apple
from goodsdex.publish import to_public
from goodsdex.archive import merge_archive


def page(sku="TEST1CH/A", price="5999.00", family="iphone", currency="CNY"):
    product = {
        "partNumber": sku,
        "familyType": "iphone_test",
        "fullPrice": "p1",
        "dimensionCapacity": "256gb",
        "dimensionColor": "black",
    }
    display = {
        "dimensionCapacity": {"256gb": {"value": "256 <small>GB</small>"}},
        "dimensionColor": {"black": {"value": "黑色"}},
        "prices": {
            "p1": {
                "priceCurrency": currency,
                "currentPrice": {"raw_amount": price},
                "amountAfterTradeIn": 999,
                "financing": "每月 250",
                "validProducts": [sku],
            }
        },
    }
    return (
        "<title>购买 iPhone Test - Apple (中国大陆)</title><script>window.PRODUCT_SELECTION_BOOTSTRAP={productSelectionData:"
        + json.dumps({"products": [product], "displayValues": display})
        + "};</script>"
    )


def capture(body=None, url="https://www.apple.com.cn/shop/buy-iphone/test"):
    return Capture.make("apple_cn", url, page() if body is None else body)


def test_exact_sku_price_not_installment_or_tradein():
    record = apple.parse_product(capture(), "iphone")[0]
    public = to_public(record)
    assert public["price"] == 5999
    assert public["id"] == "CN:apple_cn:commodity:TEST1CH/A"
    assert public["product_id"] == "CN:apple_cn:product:iphone_test"
    assert public["currency"] == "CNY" and public["price_kind"] == "sku"
    price_assert = next(a for a in record["assertions"] if a["attribute"] == "price")
    assert price_assert["locator"].endswith('.prices["p1"].currentPrice.raw_amount')
    assert price_assert["capture_id"] == record["captures"][0]["capture_id"]
    assert price_assert["raw_value"] == "5999.00"
    assert price_assert["normalized_value"] == 5999


def test_separate_colour_and_capacity_records_in_archive(tmp_path):
    a = apple.parse_product(capture(), "iphone")[0]
    b = apple.parse_product(capture(page("TEST2CH/A", "6999")), "iphone")[0]
    assert a["product"]["product_id"] == b["product"]["product_id"]
    merge_archive("Apple_iphone", [a, b], archive_dir=tmp_path)
    saved = json.loads((tmp_path / "Apple_iphone.json").read_text())["items"]
    assert len(saved) == 2


def test_no_price_is_not_zero_and_other_currency_rejected():
    for price, currency in [
        (None, "CNY"),
        ("0", "CNY"),
        ("NaN", "CNY"),
        ("999", "USD"),
    ]:
        rec = apple.parse_product(
            capture(page(price=price, currency=currency)), "iphone"
        )[0]
        assert rec["view"]["values"]["price"] is None
        assert not any(a["attribute"] == "price" for a in rec["assertions"])


def test_model_specific_price_key_must_include_sku():
    body = page().replace(
        '"validProducts": ["TEST1CH/A"]', '"validProducts": ["OTHERCH/A"]'
    )
    assert (
        apple.parse_product(capture(body), "iphone")[0]["view"]["values"]["price"]
        is None
    )


def test_mainland_only_and_no_guessing_empty():
    import pytest

    for u in [
        "https://www.apple.com/shop/buy-iphone/test",
        "https://www.apple.com.cn.evil.test/a",
        "http://www.apple.com.cn/store",
        "https://www.apple.com.cn:443/store",
    ]:
        with pytest.raises(ValueError):
            apple.official_url(u)
    assert apple.shop_target("/cn/shop/goto/buy_airpods/airpods_pro_3")[0] == "airpods"
    assert apple.shop_target("/cn/shop/goto/buy_accessories") is None
    for body in ["<html>challenge</html>", 'productSelectionData:{"products":[]}']:
        with pytest.raises(ValueError):
            apple.parse_product(capture(body), "iphone")
    with pytest.raises(ValueError):
        apple.parse_product(capture(page("TEST1LL/A")), "iphone")


def test_watch_and_mac_starting_price_not_claimed_full_configuration():
    for family in ["watch", "mac"]:
        assert (
            apple.parse_product(capture(), family)[0]["product"]["price_kind"]
            == "starting"
        )
    assert apple.amount("RMB 5999") is None


def test_mac_and_watch_shape_and_configurable_without_sku():
    data = {
        "products": [
            {
                "btrOrFdPartNumber": "MAC1CH/A",
                "dimensions": {"chassis-dimensionColor": "silver"},
                "priceKey": "mac",
                "productConfiguration": {"memory": "065-code"},
            },
            {"aosContainerPartNumber": "RO_X", "type": "CONFIGURABLE"},
        ],
        "mainDisplayValues": {
            "chassis-dimensionColor": {"silver": {"header": "银色"}},
            "prices": {"mac": {"currentPrice": {"raw_amount": "9999.00"}}},
        },
    }
    body = (
        "<title>购买 Mac Test - Apple (中国大陆)</title>productSelectionData:"
        + json.dumps(data)
    )
    records = apple.parse_product(capture(body), "mac")
    assert len(records) == 1 and records[0]["view"]["values"]["price"] == 9999
    assert (
        records[0]["product"]["variant_attrs"]["chassis-dimensionColor"]["label"]
        == "银色"
    )
    data["products"] = [{"part": "WATCH1CH/B", "dimensions": {}, "priceKey": "mac"}]
    records = apple.parse_product(
        capture(
            "<title>购买 Watch Test - Apple (中国大陆)</title>productSelectionData:"
            + json.dumps(data)
        ),
        "watch",
    )
    assert records[0]["product"]["part_number"] == "WATCH1CH/B"


def test_specs_model_columns_preserved_not_joined():
    body = '<div role="table" class="techspecs"><div role="row"><div role="columnheader">Pro</div><div role="columnheader">Max</div></div><div role="row"><div role="rowheader">重量</div><div role="cell">190 克</div><div role="cell">220 克</div></div></div>'
    result = apple.parse_specs(body)
    assert result["columns"] == ["Pro", "Max"]
    assert result["rows"] == [{"label": "重量", "cells": ["190 克", "220 克"]}]
    assert result["scope"] == "family_table"
    assert apple.parse_specs("<html>not specs</html>") is None


def test_full_raw_externalized_and_hash_verifiable(tmp_path):
    cap = capture()
    original = cap.response_raw
    apple.externalize(cap, tmp_path)
    assert Path(cap.raw_ref).read_text() == original
    assert cap.response_raw.startswith("<externalized:")
    import hashlib

    assert hashlib.sha256(original.encode()).hexdigest()[:16] == cap.response_hash


def test_failed_page_keeps_old_price_timestamp_and_published_other_brand(tmp_path):
    cats = tmp_path / "categories"
    cats.mkdir()
    out = tmp_path / "public"
    out.mkdir()
    old = apple.parse_product(capture(), "iphone")[0]
    (cats / "Apple_iphone.json").write_text(json.dumps([old]))
    other = {"id": "CN:mi_cn:product:1", "gid": 123, "name": "小米", "price": 1}
    (out / "goods.json").write_text(json.dumps([other]))

    def fail(url):
        if url.endswith("/shop/buy-iphone"):
            return capture('<a href="/shop/buy-iphone/test">test</a>', url)
        return Capture.make(
            "apple_cn", url, status=CaptureStatus.RATE_LIMITED, error="HTTP 429"
        )

    report = crawl(
        cats,
        tmp_path / "apple" / "raw",
        tmp_path / "archive",
        ["iphone"],
        transport=fail,
        pause=0,
    )
    assert report["errors"] > 0
    assert json.loads((cats / "Apple_iphone.json").read_text()) == [old]
    publish_apple(cats, out)
    first = (
        out / "prices" / "apple" / (report["fetched_at"][:7] + ".jsonl")
    ).read_text()
    publish_apple(cats, out)
    assert (
        out / "prices" / "apple" / (report["fetched_at"][:7] + ".jsonl")
    ).read_text() == first
    items = json.loads((out / "goods.json").read_text())
    assert other in items
    assert (
        next(i for i in items if i["id"].startswith("CN:apple"))["fetched_at"]
        == old["fetched_at"]
    )


def test_daily_rebuild_keeps_apple_source_contract(tmp_path):
    from goodsdex.publish import build

    cats = tmp_path / "cats"
    cats.mkdir()
    (cats / "Apple_iphone.json").write_text(
        json.dumps(apple.parse_product(capture(), "iphone"))
    )
    build(cats, tmp_path / "out")
    row = json.loads((tmp_path / "out" / "goods.json").read_text())[0]
    assert row["source"] == "apple_cn" and row["part_number"] == "TEST1CH/A"
    assert row["price_kind"] == "sku"


def test_price_parse_gap_keeps_previous_quote_and_evidence(tmp_path):
    cats = tmp_path / "cats"
    cats.mkdir()
    old = apple.parse_product(capture(), "iphone")[0]
    old["fetched_at"] = "2026-10-01T10:00:00+08:00"
    old["product"]["price_fetched_at"] = old["fetched_at"]
    (cats / "Apple_iphone.json").write_text(json.dumps([old]))

    def transport(url):
        if url.endswith("/shop/buy-iphone"):
            return capture('<a href="/shop/buy-iphone/test">Test</a>', url)
        if url.endswith("/iphone/"):
            return capture("<html>Index</html>", url)
        return capture(page(price=None), url)

    crawl(
        cats,
        tmp_path / "raw",
        tmp_path / "archive",
        ["iphone"],
        transport=transport,
        pause=0,
    )
    saved = json.loads((cats / "Apple_iphone.json").read_text())[0]
    assert saved["view"]["values"]["price"] == 5999
    assert saved["product"]["price_status"] == "stale"
    assert saved["product"]["price_fetched_at"] == old["fetched_at"]
    assertion = next(a for a in saved["assertions"] if a["attribute"] == "price")
    assert any(c["capture_id"] == assertion["capture_id"] for c in saved["captures"])
    publish_apple(cats, tmp_path / "public")
    latest = json.loads(
        (tmp_path / "public" / "prices" / "apple" / "latest.json").read_text()
    )
    assert (
        latest["prices"][saved["product"]["variant_id"]]["fetched_at"]
        == old["fetched_at"]
    )


def test_hourly_mi_refresh_never_sends_apple_sku_to_mi(tmp_path, monkeypatch):
    import runpy, sys

    out = tmp_path / "public"
    out.mkdir()
    apple_row = to_public(apple.parse_product(capture(), "iphone")[0])
    apple_row["gid"] = "LEGACY-APPLE-ID"
    (out / "goods.json").write_text(
        json.dumps([{"id": "CN:mi_cn:product:1", "gid": 123, "price": 10}, apple_row])
    )
    requested = []

    def refresh(gids, store):
        requested.extend(gids)
        return {"updated": 0, "errors": []}

    module = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts" / "ci_refresh_prices.py")
    )
    monkeypatch.setattr(sys, "argv", ["ci_refresh_prices.py", "--public", str(out)])
    module["main"].__globals__["refresh"] = refresh
    assert module["main"]() == 0
    assert requested == ["123"]
    assert apple_row in json.loads((out / "goods.json").read_text())


def test_prices_only_reuses_urls_and_preserves_specs(tmp_path):
    cats = tmp_path / "cats"
    cats.mkdir()
    old = apple.parse_product(capture(), "iphone")[0]
    old["view"]["values"]["specs_table"] = {
        "scope": "family_table",
        "columns": ["Test"],
        "rows": [],
    }
    old["assertions"].append(
        apple._assert(
            capture(),
            old["product"]["variant_id"],
            "specs_table",
            old["view"]["values"]["specs_table"],
            "html:table",
        ).to_dict()
    )
    (cats / "Apple_iphone.json").write_text(json.dumps([old]))
    seen = []

    def transport(url):
        seen.append(url)
        return capture(page(price="5888.00"), url)

    report = crawl(
        cats,
        tmp_path / "raw",
        tmp_path / "archive",
        ["iphone"],
        transport=transport,
        pause=0,
        prices_only=True,
    )
    saved = json.loads((cats / "Apple_iphone.json").read_text())[0]
    assert seen == [old["product"]["source_url"]]
    assert saved["view"]["values"]["price"] == 5888
    assert (
        saved["view"]["values"]["specs_table"] == old["view"]["values"]["specs_table"]
    )
    assert report["prices_only"] is True


def test_cli_prices_only_reaches_crawler(tmp_path, monkeypatch):
    import runpy, sys

    module = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts" / "crawl_apple.py")
    )
    options = {}

    def fake(*args, **kwargs):
        options.update(kwargs)
        return {"errors": 0, "variants": 1}

    module["main"].__globals__["crawl"] = fake
    monkeypatch.setattr(
        sys, "argv", ["crawl_apple.py", "--prices-only", "--family", "iphone"]
    )
    assert module["main"]() == 0
    assert options["prices_only"] is True
