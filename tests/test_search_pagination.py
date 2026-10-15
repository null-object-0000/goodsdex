"""分页必须越过旧的 20 页边界，未覆盖时不能声称完整。"""
import json
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

import pytest

from goodsdex.sources import mi_cn


def response(total, pids):
    return 'cb(' + json.dumps({"code": 200, "data": {
        "total": total, "pc_list": [{"product_id": str(p), "commodity_list": [{"name": str(p)}]}
                                    for p in pids]}}) + ')'


def test_default_enumeration_exceeds_twenty_pages():
    pages = []

    def get(url):
        page = int(parse_qs(urlparse(url).query)["page_index"][0])
        pages.append(page)
        return response(778, range((page - 1) * 20, min(page * 20, 778)))

    with patch.object(mi_cn, "_get", side_effect=get):
        e = mi_cn.enumerate_products("家电", pause=0)
    assert len(e["items"]) == 778
    assert pages == list(range(1, 40))
    assert e["discovery"]["pages_fetched"] == 39
    assert e["discovery"]["completeness"] == "complete"
    assert e["discovery"]["stop_reason"] == "reached_total"


def test_explicit_page_cap_remains_partial():
    with patch.object(mi_cn, "_get", side_effect=[response(3, [1]), response(3, [2])]):
        e = mi_cn.enumerate_products("x", max_pages=2, pause=0)
    assert e["discovery"]["completeness"] == "partial"
    assert e["discovery"]["stop_reason"] == "max_pages_reached"
    assert e["discovery"]["pages_fetched"] == 2


@pytest.mark.parametrize("tail,reason", [
    ([response(3, []), response(3, [])], "no_sellable_items"),
    ([response(3, [1, 2])], "no_new_items"),
])
def test_early_stop_short_of_total_remains_partial(tail, reason):
    with patch.object(mi_cn, "_get", side_effect=[response(3, [1, 2])] + tail):
        e = mi_cn.enumerate_products("x", pause=0)
    assert len(e["items"]) == 2
    assert e["discovery"]["completeness"] == "partial"
    assert e["discovery"]["stop_reason"] == reason


def test_error_after_some_results_is_failed():
    with patch.object(mi_cn, "_get", side_effect=[response(3, [1]), OSError("断网")]):
        e = mi_cn.enumerate_products("x", pause=0)
    assert len(e["items"]) == 1
    assert e["discovery"]["completeness"] == "failed"


def test_crawl_runner_passes_larger_default_cap(tmp_path):
    import crawl_all

    with patch("sys.argv", ["crawl_all.py", "家电"]), \
         patch.object(crawl_all, "OUT", tmp_path), \
         patch.object(crawl_all, "load_progress", return_value={}), \
         patch.object(crawl_all, "save_progress"), \
         patch.object(crawl_all.mi_cn, "list_categories", return_value={"家电": "家电"}), \
         patch.object(crawl_all.pipeline, "run_category", return_value=[]) as run:
        assert crawl_all.main() == 0
    assert run.call_args.kwargs["max_pages"] == 100


def test_pipeline_cli_passes_larger_default_cap():
    from goodsdex import pipeline

    with patch.object(pipeline, "run_category") as run:
        assert pipeline.main(["--category", "家电"]) == 0
    assert run.call_args.args[2] == 100
