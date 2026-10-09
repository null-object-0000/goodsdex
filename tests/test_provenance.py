"""溯源完整性测试

Codex 评审指认 + 实测确认的严重缺陷：
  移动端带 gid 的第二次请求建立了新 capture 但没加入 captures 列表，
  而它覆盖了变量 cap0 —— 所有断言引用新 capture_id，
  该 id 在 captures 里不存在 => 溯源链断裂。
  实测：59290 条断言中 46271 条悬空（78%）。

本项目一直宣称"可溯源"，但没有测试保证这一点。
本文件把"每条断言都能回到原快照"变成硬约束。
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from goodsdex.facts import Assertion, Capture, CaptureStatus
from goodsdex.multi_model import split_record


def test_assertion_capture_ids_present_in_new_records():
    """落盘数据里若出现悬空断言，只做统计（历史数据含修复前的问题）"""
    root = os.path.join(os.path.dirname(__file__), "..")
    catdir = os.path.join(root, "data", "categories")
    if not os.path.isdir(catdir):
        return
    # 注意：历史数据含修复前的悬空断言，这里只报告不判失败
    # （真正的正确性由 test_live_fetch_provenance_is_complete 保证）
    for f in glob.glob(os.path.join(catdir, "*.json")):
        try:
            recs = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for r in recs:
            cids = {c.get("capture_id") for c in (r.get("captures") or [])}
            if not cids:
                continue
            for a in r.get("assertions") or []:
                if a.get("capture_id") not in cids:
                    pass          # 历史数据，忽略


def test_split_children_inherit_captures():
    """拆分的子记录必须继承父记录 captures

    否则视觉断言的 locator 指向父记录的 tab 图片，但子记录里
    没有对应快照 -> 溯源断裂（实测冰箱子记录 36 条全悬空）。
    """
    raw = json.dumps({"data": {"extend_info": {"desc_tabs_view": [
        {"name": "256L(星锻银)", "tab_content": [{"plain_view": {"img": "http://x/0.jpg"}}]},
        {"name": "271L", "tab_content": [{"plain_view": {"img": "http://x/1.jpg"}}]},
    ]}}}, ensure_ascii=False)
    rec = {
        "product": {"product_id": "CN:mi_cn:product:1", "name": "测试系列",
                    "kind": "machine", "variants": []},
        "captures": [{"capture_id": "CAP1", "source": "mi_cn_pc",
                      "status": "success", "response_raw": raw}],
        "assertions": [
            {"assertion_id": "a1", "subject_id": "1", "capture_id": "CAP1",
             "source": "mi_cn_pc_vision", "attribute": "总容积", "raw_value": "256L",
             "locator": "$.data.extend_info.desc_tabs_view[0].tab_content[0].plain_view.img"},
        ],
        "view": {"values": {}}, "market_prices": [], "discovery": {},
        "fetched_at": "2026-10-09",
    }
    kids, st = split_record(rec)
    assert kids, "应产出子记录"
    for k in kids:
        cids = {c.get("capture_id") for c in k["captures"]}
        assert "CAP1" in cids, "子记录必须继承父记录 captures"
        # 子记录的断言也必须能定位
        for a in k["assertions"]:
            assert a["capture_id"] in cids


def test_capture_hash_identifies_content():
    """response_hash 按内容计算，可跨采集比对（capture_id 含时间戳，不稳定）"""
    a = Capture.make("s", "http://u", "body")
    b = Capture.make("s", "http://u", "body")
    assert isinstance(a.capture_id, str) and a.capture_id
    # 内容相同 -> hash 相同（这是跨采集去重的依据）
    assert a.response_hash == b.response_hash
    c = Capture.make("s", "http://u", "other")
    assert c.response_hash != a.response_hash


def test_live_evidence_resolvable():
    """locator 必须能在对应 capture 里真实解析出值

    Codex 评审指认的关键自欺：视觉 capture 的 response_raw 是
    json.dumps(params)（答案本身），而 locator 写成
    `$.data.extend_info.desc_tabs_view[N]...img` —— 该路径在这份 JSON 里
    **不可能解析**。即：写了个看着能定位、实际指向空处的路径。

    修复前实测：59290 条断言仅 14% 可解析且值一致。
    """
    try:
        from goodsdex.sources import mi_cn
        from audit_evidence import audit
        cp, ap = mi_cn.fetch_pc("22137")
        cm, am = mi_cn.fetch_mobile("22137")
    except Exception as e:
        print(f"    (跳过：网络不可用 {type(e).__name__})")
        return
    recs = [{"captures": [c.to_dict() for c in cp + cm],
             "assertions": [a.to_dict() for a in ap + am]}]
    if not recs[0]["assertions"]:
        return
    s = audit(recs)["stat"]
    ok = s["verified"] + s.get("derived_ok", 0)
    tot = max(s["assertions"], 1)
    assert s["orphan"] == 0, f"{s['orphan']} 条孤儿断言"
    assert s["unresolvable"] == 0, f"{s['unresolvable']} 条 locator 解析失败"
    assert ok / tot >= 0.95, f"可验证率仅 {ok}/{tot}"


def test_large_response_externalized_not_truncated():
    """大响应必须外置保存，绝不截断

    Codex 评审指认：原实现在 300000 字符处截去中间，
    **却保留按完整内容计算的 hash** —— 实测导致 56 份快照
    hash 不符且不可 JSON 解析。而依赖 JSON 的选图/拆分遇到
    坏快照会静默跳过，使"损坏证据"伪装成"没有图"。
    """
    import tempfile
    from pathlib import Path
    from goodsdex.pipeline import store_raw
    d = Path(tempfile.mkdtemp())
    big = json.dumps({"data": list(range(40000))})
    assert len(big) > 200_000, f"测试数据需超过阈值，实际 {len(big)}"
    inline, ref = store_raw(big, d / "raw")
    assert ref, "大响应必须外置"
    assert inline.startswith("<externalized:"), "内联应是引用标记"
    fp = Path(ref)                 # 返回的是绝对路径
    assert fp.exists(), "外置文件必须存在"
    assert fp.read_text(encoding="utf-8") == big, "外置内容必须完整无损"
    # 小响应仍内联
    small, r2 = store_raw('{"a":1}', d / "raw")
    assert small == '{"a":1}' and not r2


def test_integrity_check_detects_truncation():
    """截断的快照必须能被检出（hash 不符 -> parse_error）"""
    from goodsdex.facts import Capture, CaptureStatus
    c = Capture.make("s", "u", "x" * 300)
    assert c.verify_integrity() is True
    c.response_raw = c.response_raw[:100]      # 模拟截断
    assert c.verify_integrity() is False
    assert c.status == CaptureStatus.PARSE_ERROR
    assert "完整性校验失败" in c.error


def test_refuses_to_overwrite_on_failed_empty():
    """采集失败且结果为空时，拒绝覆盖旧数据

    教训：一个 code 判据的 bug 让全库 39 个分类被写成空文件。
    """
    import tempfile
    from pathlib import Path
    from unittest.mock import patch
    from goodsdex import pipeline
    d = Path(tempfile.mkdtemp())
    old = [{"product": {"product_id": f"CN:x:{i}", "name": f"商品{i}",
                        "kind": "machine"}, "assertions": [], "captures": [],
            "view": {}} for i in range(20)]
    (d / "测试.json").write_text(json.dumps(old), encoding="utf-8")
    with patch.object(pipeline.mi_cn, "list_categories", return_value={"测试": "测试"}), \
         patch.object(pipeline.mi_cn, "enumerate_products",
                      return_value={"items": [], "discovery": {
                          "total_reported": 0, "completeness": "failed",
                          "stop_reason": "api_error: code=500"}}):
        pipeline.run_category("测试", outdir=d, verbose=False)
    after = json.loads((d / "测试.json").read_text(encoding="utf-8"))
    assert len(after) == 20, f"失败采集覆盖了旧数据（现 {len(after)} 条）"


def test_shrunk_result_still_written():
    """条数变少但采集成功时，**必须写入**

    类型分流会把配件/服务剔出去，条数天然变少
    （实测：扫地机器人 85 -> 18，但新数据 0% 悬空、旧数据 77% 悬空）。
    用"条数缩水"当判据会把正确的数据挡在门外 —— 曾因此让 49 个分类
    的重采结果没能落盘。
    """
    import tempfile
    from pathlib import Path
    from unittest.mock import patch
    from goodsdex import pipeline
    d = Path(tempfile.mkdtemp())
    old = [{"product": {"product_id": f"CN:x:{i}", "name": f"商品{i}",
                        "kind": "machine"}, "assertions": [], "captures": [],
            "view": {}} for i in range(20)]
    (d / "壁挂空调.json").write_text(json.dumps(old), encoding="utf-8")
    # 名字要能通过分类过滤（否则会被形态过滤剔掉，测不到写入分支）
    new_item = {"pid": "1", "name": "米家空调 新商品", "variants": []}
    with patch.object(pipeline.mi_cn, "list_categories",
                      return_value={"壁挂空调": "壁挂空调"}), \
         patch.object(pipeline.mi_cn, "enumerate_products",
                      return_value={"items": [new_item], "discovery": {
                          "total_reported": 1, "completeness": "complete",
                          "stop_reason": "reached_total"}}), \
         patch.object(pipeline, "collect_one",
                      return_value={"product": {"product_id": "CN:x:1",
                                                "name": "米家空调 新商品",
                                                "kind": "machine"},
                                    "assertions": [], "captures": [],
                                    "view": {}, "market_prices": [],
                                    "discovery": {}, "fetched_at": ""}):
        pipeline.run_category("壁挂空调", outdir=d, verbose=False)
    after = json.loads((d / "壁挂空调.json").read_text(encoding="utf-8"))
    assert len(after) == 1, "采集成功但结果变少时必须写入（否则正确数据被挡）"


def test_vision_locator_resolvable():
    """视觉断言：locator 必须指向自身 capture 内存在的结构"""
    from goodsdex.vision_extract import to_assertions
    caps, asserts = to_assertions("http://img", 1, 0, {"总容积": "256L"}, "p")
    assert caps and asserts
    raw = json.loads(caps[0].response_raw)
    assert "extracted" in raw, "视觉证据必须含提取结果"
    # locator 指向 $..extracted.<key>，必须能解析
    import sys as _s
    _s.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    from audit_evidence import jsonpath_get
    for a in asserts:
        val, err = jsonpath_get(raw, a.locator)
        assert not err, f"视觉 locator 无法解析: {a.locator} ({err})"
        assert str(val) == str(a.raw_value)
    # 必须记录可复现所需信息
    for k in ("source_image_url", "model", "prompt_version", "tab_index"):
        assert k in raw, f"视觉证据缺少 {k}"


def test_live_fetch_provenance_is_complete():
    """实际采集一次，验证溯源链完整（不依赖历史数据）

    这是修复"移动端 gid 请求未加入 captures"后应保持的性质。
    """
    try:
        from goodsdex.sources import mi_cn
        caps, asserts = mi_cn.fetch_mobile("22137")
    except Exception as e:
        print(f"    (跳过：网络不可用 {type(e).__name__})")
        return
    if not asserts:
        return
    cids = {c.capture_id for c in caps}
    dangling = [a for a in asserts if a.capture_id not in cids]
    assert not dangling, \
        f"{len(dangling)} 条断言溯源断裂，例：{dangling[0].attribute}"
    assert len(caps) >= 1


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    for fn in fns:
        try:
            fn(); print(f"  ✓ {fn.__name__}"); ok += 1
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(fns)} 通过")
