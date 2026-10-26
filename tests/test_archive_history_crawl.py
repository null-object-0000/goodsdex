"""Archive admission must depend on explicit evidence, never search/age/stock."""
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "archive_crawl", Path(__file__).resolve().parents[1] / "scripts/crawl_archive_history.py")
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


def check_admission(tmp_path):
    evidence = tmp_path / "evidence"
    evidence.mkdir()

    class FakeClient:
        rows = []
        limit = 600

        def cached(self, url, body=None, headers=None):
            row = dict(id=1, url=url, fetched_at="2026-10-26T00:00:00Z",
                       status=200, body_file="fixture", outcome="response")
            if "sitemap" in url:
                return row, "".join(f"<loc>http://item.mi.com/product/{n}.html</loc>" for n in range(1, 7))
            if body is not None:
                pid = body[1]["productId"]
                responses = {
                    "1": {"code": 400480502, "message": "该产品已下架"},
                    "2": {"code": -50011, "msg": "商品不存在或未上架"},
                    "3": {"code": 0, "data": {"is_stock": False}},
                    "4": {"code": 400480400},
                    "5": {"code": 400480502},
                }
                if pid == "5":
                    row.update(status=429, outcome="rate_limited")
                return row, json.dumps(responses[pid])
            pid = archive.urllib.parse.parse_qs(archive.urllib.parse.urlsplit(url).query)["product_id"][0]
            # Incorrect identity must not be silently associated with the requested PID.
            info = dict(product_id="999" if pid == "6" else pid, name="米家测试机型",
                        price="99", is_enable=False)
            return row, json.dumps({"data": {"product_info": info}})

    with patch.object(archive, "OUT", tmp_path), patch.object(archive, "EVIDENCE", evidence):
        assert archive.crawl(FakeClient(), target=60) == 1
    assert sorted(p.name for p in tmp_path.glob("*.json")) == ["1.json"]
    record = json.loads((tmp_path / "1.json").read_text())
    assert record["price"] is None
    assert record["last_seen_on_sale"] is None
    assert record["model"] is None and record["params"] == []
    assert record["last_known_price"] == "99"
    assert record["discontinued_evidence"]["business_code"] == 400480502
    observations = json.loads((evidence / "crawl-observations.json").read_text())
    assert observations[4]["outcome"] == "rate_limited"
    assert observations[5]["outcome"] == "identity_missing"


class ArchiveAdmissionTests(unittest.TestCase):
    def test_explicit_evidence_required(self):
        with tempfile.TemporaryDirectory() as d:
            check_admission(Path(d))

    def test_tv_size_panel_and_prices_do_not_leak(self):
        raw = """<script>var MITV_SPECS_TYPE = '55';</script>
        <div class="mitv-specs-43"><table><tr><td>分辨率</td><td>1920*1080</td></tr></table></div>
        <div class="mitv-specs-55"><table>
          <tr><td>分辨率</td><td>3840*2160</td></tr>
          <tr><td>价格</td><td>1999元</td></tr>
        </table></div>
        <div class="site-footer"><dl><dt>帮助中心</dt><dd>客服电话</dd></dl></div>"""
        params, status = archive.parse_specs(raw)
        self.assertEqual(status, "text_pairs_extracted")
        self.assertEqual([(p["label"], p["value"]) for p in params], [("分辨率", "3840*2160")])
        params, status = archive.parse_specs(raw.replace("var MITV_SPECS_TYPE = '55';", ""))
        self.assertEqual((params, status), ([], "ambiguous_variant"))

    def test_accessory_model_is_not_assigned_to_main_product(self):
        params, status = archive.parse_specs("""
        <p><b>型号</b><span>DDYS01SKS</span></p>
        <h3>替换刷头</h3><p><b>产品型号</b><span>DDYST01SKS</span></p>""")
        self.assertEqual((params, status), ([], "ambiguous_multiple_models"))


if __name__ == "__main__":
    unittest.main()
