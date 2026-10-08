"""全库分析：类型分流、质量体检、代际线索。

用法:
  PYTHONPATH=src python3 scripts/analyze_all.py
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from goodsdex.coverage import coverage_report
from goodsdex.kind import classify_product_kind

CATS = ROOT / "data" / "categories"


def main() -> int:
    files = sorted(CATS.glob("*.json"))
    total = 0
    kinds = Counter()
    cats_summary = []
    all_kinds = {"machine": [], "accessory": [], "service": [], "unknown": []}
    no_param, partial_cap, no_price = [], [], []

    for f in files:
        try:
            recs = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  读取失败 {f.name}: {e}")
            continue
        cat = f.stem
        km = {"machine": 0, "accessory": 0, "service": 0, "unknown": 0}
        for r in recs:
            nm = (r.get("product") or {}).get("name", "")
            k = (r.get("product") or {}).get("kind") or classify_product_kind(nm, cat)
            km[k] += 1
            kinds[k] += 1
            all_kinds[k].append((cat, nm, r))
            v = r.get("view") or {}
            if v.get("values", {}).get("_params_empty"):
                no_param.append((cat, nm))
            elif not v.get("values"):
                no_param.append((cat, nm))
            caps = r.get("captures") or []
            if caps and any(c.get("status") != "success" for c in caps):
                partial_cap.append((cat, nm))
            if "price" not in (v.get("values") or {}):
                no_price.append((cat, nm))
        total += len(recs)
        cats_summary.append((cat, len(recs), km["machine"], km["accessory"],
                             km["service"], km["unknown"]))

    print("=" * 78)
    print(f"全库：{len(files)} 个分类，{total} 款商品")
    print(f"类型分流：整机 {kinds['machine']} | 配件耗材 {kinds['accessory']} "
          f"| 服务 {kinds['service']} | 未判定 {kinds['unknown']}")
    print("=" * 78)
    print(f"\n{'分类':22s}{'总数':>6s}{'整机':>6s}{'配件':>6s}{'服务':>6s}{'未判':>6s}")
    for c, n, m, a, s, u in sorted(cats_summary, key=lambda x: -x[1]):
        flag = "  ⚠混入服务/配件" if (s + a) > n * 0.5 and m > 0 else ""
        print(f"{c[:20]:22s}{n:>6d}{m:>6d}{a:>6d}{s:>6d}{u:>6d}{flag}")

    print("\n" + "=" * 78)
    print("质量体检")
    print("=" * 78)
    print(f"  无参数（官方接口未给）  {len(no_param):5d} 款"
          f"  ({len(no_param)/max(total,1):.1%})")
    print(f"  采集源有失败            {len(partial_cap):5d} 款"
          f"  ({len(partial_cap)/max(total,1):.1%})")
    print(f"  无价格                  {len(no_price):5d} 款"
          f"  ({len(no_price)/max(total,1):.1%})")

    if no_param[:8]:
        print("\n  无参数示例（这些是官方接口确实没给，非采集失败）：")
        for c, n in no_param[:8]:
            print(f"    [{c}] {n[:44]}")

    # 整机里有参数的，做覆盖度
    machine_total = len(all_kinds["machine"])
    print(f"\n  整机 {machine_total} 款是换代分析的可用对象")

    # 抽样一个品类的覆盖度
    for cat in ("吹风机", "扫地机器人", "Xiaomi 数字旗舰"):
        p = CATS / f"{cat}.json"
        if p.exists():
            recs = json.loads(p.read_text(encoding="utf-8"))
            k = classify_product_kind
            machines = [r for r in recs
                        if (r.get("product") or {}).get("kind") == "machine"
                        or k((r.get("product") or {}).get("name", ""), cat) == "machine"]
            if machines:
                rep = coverage_report(machines, cat)
                s = rep["summary"]
                print(f"\n  【{cat}】整机 {len(machines)} 款")
                print(f"    采集成功率 {s['capture_success_rate']:.0%} | "
                      f"关键属性覆盖 {s['key_attr_coverage_avg']:.0%} | "
                      f"身份确认 {s['identity_verified_rate']:.0%}")

    # 落盘
    out = ROOT / "data" / "_analysis.json"
    out.write_text(json.dumps({
        "categories": len(files), "products": total,
        "kinds": dict(kinds),
        "no_params": len(no_param), "capture_failures": len(partial_cap),
        "no_price": len(no_price),
        "per_category": [{"category": c, "total": n, "machine": m, "accessory": a,
                          "service": s, "unknown": u}
                         for c, n, m, a, s, u in cats_summary],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
