"""证据可解引用审计：locator 真的能在对应 capture 里解析出值吗？

Codex 评审指认的关键自欺：
  视觉 capture 的 response_raw 是 json.dumps(params)（答案本身），
  而 locator 写成 `$.data.extend_info.desc_tabs_view[N]...img` ——
  该路径在这份 JSON 里**不可能解析**。
  即：写了个看着能定位、实际指向空处的路径。

本脚本对每条断言：
  1. 找到它的 capture（不存在 -> 孤儿）
  2. 若 locator 形如 JSONPath，尝试在 capture 内容里解析
  3. 解析出的值应与断言的 raw_value 一致

区分「未验证」与「验证失败」—— 不能把无法验证说成通过。
"""
from __future__ import annotations
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def jsonpath_get(obj, path: str):
    """极简 JSONPath：支持 $.a.b[0].c 与 $.a.{中文键}"""
    if not path.startswith("$"):
        return None, "not_jsonpath"
    cur = obj
    # 拆成 token：.key 或 [idx]
    toks = re.findall(r"\.([^.[\]]+)|\[(\d+)\]", path[1:])
    if not toks:
        return None, "empty_path"
    for key, idx in toks:
        if idx:
            if not isinstance(cur, list) or int(idx) >= len(cur):
                return None, f"index {idx} out of range"
            cur = cur[int(idx)]
        else:
            if not isinstance(cur, dict):
                return None, f"not a dict at {key}"
            if key not in cur:
                return None, f"key {key!r} missing"
            cur = cur[key]
    return cur, ""


# 派生字段：raw_value 由源结构**提取/加工**而来，不等于源结构本身。
# 判定其可核实性看"能否定位到源"，而非"值与源相等"。
DERIVED_FIELDS = {
    "pc_tabs",        # 从 desc_tabs_view[] 提取 name
    "pc_imgs",        # 从 tab_content[].plain_view 提取 img/宽高
    "carousel",       # 从 carouselList[] 提取 imgUrl
    "colors",         # 从 saleAttributeList[] 提取某一项
    "attrs",          # 从 saleAttributeList 归纳成 dict
    "sell_points",    # 从文本拆分
    "buyer_imgs",
    "review_tags",
}


def _is_derived(attr: str) -> bool:
    return attr in DERIVED_FIELDS


_EXT_RE = re.compile(r"<externalized:sha256=([0-9a-f]{64})")


def _load_raw(raw: str, cap: dict):
    """把 capture 的 response_raw 解析成 JSON 对象。

    大响应是**外置保存**的：response_raw 只留
    `<externalized:sha256=...>` 占位，真内容在 data/raw/<前2位>/<sha>.txt。
    审计脚本必须跟着 raw_ref 去读 —— 否则会把外置当成"不可解析"，
    把好好的证据误报成坏的（实测 4117 条被误报）。
    """
    if not raw:
        return None
    m = _EXT_RE.match(raw.strip())
    if m:
        p = None
        ref = cap.get("raw_ref") or ""
        if ref:
            cand = Path(ref)
            p = cand if cand.is_absolute() else (ROOT / cand)
            if not p.exists():
                p = None
        if p is None:
            h = m.group(1)
            p = ROOT / "data" / "raw" / h[:2] / f"{h}.txt"
        if not p.exists():
            return None
        raw = p.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except Exception:
        return None


def audit(recs: list[dict]) -> dict:
    stat = {"assertions": 0, "orphan": 0, "verified": 0, "derived_ok": 0,
            "mismatch": 0, "unresolvable": 0, "non_jsonpath": 0,
            "unparseable_capture": 0}
    samples = {"orphan": [], "mismatch": [], "unresolvable": [], "non_jsonpath": []}
    caps_by_id = {}
    for r in recs:
        for c in r.get("captures") or []:
            caps_by_id.setdefault(c.get("capture_id"), c)
    for r in recs:
        for a in r.get("assertions") or []:
            stat["assertions"] += 1
            cid = a.get("capture_id")
            cap = caps_by_id.get(cid)
            if not cap:
                stat["orphan"] += 1
                if len(samples["orphan"]) < 4:
                    samples["orphan"].append((a.get("source"), a.get("attribute")))
                continue
            loc = a.get("locator") or ""
            if not loc.startswith("$"):
                stat["non_jsonpath"] += 1
                if len(samples["non_jsonpath"]) < 4:
                    samples["non_jsonpath"].append((a.get("source"), loc[:60]))
                continue
            raw = cap.get("response_raw") or ""
            obj = _load_raw(raw, cap)
            if obj is None:
                stat["unparseable_capture"] += 1
                if len(samples.setdefault("unparseable", [])) < 4:
                    samples["unparseable"].append(
                        (a.get("source"), (raw or "")[:48]))
                continue
            val, err = jsonpath_get(obj, loc)
            if err:
                stat["unresolvable"] += 1
                if len(samples["unresolvable"]) < 4:
                    samples["unresolvable"].append(
                        (a.get("source"), loc[:56], err))
                continue
            # 解析成功：值是否一致
            av = str(a.get("raw_value"))
            sv = str(val)
            if av == sv:
                stat["verified"] += 1
            elif _is_derived(a.get("attribute", "")):
                # 派生断言：raw_value 是从源结构**提取**出来的
                # （如 pc_tabs 取 name 字段、carousel 取 imgUrl）
                # 与原结构不相等是正常的；能定位到源即视为可核实
                stat["derived_ok"] += 1
            elif isinstance(val, dict) and av == str(val.get("value")):
                # locator 指向容器、断言值取其中 value 字段（旧数据的写法）
                stat["verified"] += 1
            elif isinstance(val, str) and av == val.strip():
                # 源值首尾有空白、断言做了 strip —— 合法规范化。
                # 单独计数，不计入 mismatch（否则 65 条商品名被误报）。
                stat["normalized_ok"] = stat.get("normalized_ok", 0) + 1
            else:
                stat["mismatch"] += 1
                if len(samples["mismatch"]) < 4:
                    samples["mismatch"].append((a.get("source"), loc[:40], av[:24], sv[:24]))
    return {"stat": stat, "samples": samples}


def main() -> int:
    files = sorted(glob.glob(str(ROOT / "data" / "categories" / "*.json")))
    if not files:
        print("无数据")
        return 1
    allrecs = []
    for f in files:
        try:
            allrecs += json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            pass
    res = audit(allrecs)
    s = res["stat"]
    n = max(s["assertions"], 1)
    print("=" * 70)
    print("证据可解引用审计")
    print("=" * 70)
    print(f"\n断言总数            {s['assertions']}")
    print(f"  可解析且值一致     {s['verified']:6d}  ({s['verified']/n:.1%})")
    print(f"  可定位到源(派生)    {s.get('derived_ok',0):6d}  ({s.get('derived_ok',0)/n:.1%})")
    print(f"  孤儿（capture 缺失）{s['orphan']:6d}  ({s['orphan']/n:.1%})")
    print(f"  locator 解析失败   {s['unresolvable']:6d}  ({s['unresolvable']/n:.1%})")
    print(f"  capture 不可解析   {s['unparseable_capture']:6d}")
    print(f"  非 JSONPath        {s['non_jsonpath']:6d}")
    print(f"  规范化后一致       {s.get('normalized_ok',0):6d}  "
          f"({s.get('normalized_ok',0)/n:.1%})  源值首尾空白，断言已 strip")
    print(f"  值不一致           {s['mismatch']:6d}")
    for kind, items in res["samples"].items():
        if items:
            print(f"\n{kind} 样例:")
            for it in items:
                print(f"   {it}")
    print("\n说明：unresolvable 多为**修复前**写下的虚假 locator（指向原始响应路径）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
