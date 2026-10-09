"""溯源完整性审计：每条断言是否都能回到原快照？

由来（Codex 评审指认，实测确认）：
  移动端带 gid 的第二次请求建立了新 capture 但没加入 captures 列表，
  而它覆盖了变量 cap0 —— 所有断言引用新 capture_id，
  该 id 在 captures 里不存在 => **溯源链断裂**。
  实测抽样：5196 条断言只有 23% 可定位（77% 悬空）。

这个脚本把"可溯源"从口号变成可验证的指标。
"""
from __future__ import annotations
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit_file(fp: Path) -> dict:
    recs = json.loads(fp.read_text(encoding="utf-8"))
    tot = ok = 0
    dangling = {}
    for r in recs:
        cids = {c.get("capture_id") for c in (r.get("captures") or [])}
        for a in r.get("assertions") or []:
            tot += 1
            if a.get("capture_id") in cids:
                ok += 1
            else:
                src = a.get("source", "?")
                dangling[src] = dangling.get(src, 0) + 1
    return {"file": fp.name, "total": tot, "ok": ok,
            "dangling": dangling,
            "rate": round(ok / tot, 4) if tot else 1.0}


def main() -> int:
    files = sorted(glob.glob(str(ROOT / "data" / "categories" / "*.json")))
    if not files:
        print("没有数据文件")
        return 1
    grand_t = grand_o = 0
    bad, per_src = [], {}
    for f in files:
        try:
            r = audit_file(Path(f))
        except Exception as e:
            print(f"  ✗ {Path(f).name}: {type(e).__name__}: {e}")
            continue
        grand_t += r["total"]
        grand_o += r["ok"]
        for s, n in r["dangling"].items():
            per_src[s] = per_src.get(s, 0) + n
        if r["rate"] < 0.999 and r["total"]:
            bad.append(r)

    print("=" * 68)
    print("溯源完整性审计")
    print("=" * 68)
    print(f"\n断言总数 {grand_t}")
    print(f"可定位   {grand_o} ({grand_o/max(grand_t,1):.1%})")
    print(f"悬空     {grand_t-grand_o} ({(grand_t-grand_o)/max(grand_t,1):.1%})")
    if per_src:
        print("\n悬空按来源分：")
        for s, n in sorted(per_src.items(), key=lambda x: -x[1]):
            print(f"   {s:20s} {n}")
    if bad:
        print(f"\n有问题的分类文件 {len(bad)} 个（前 8）：")
        for r in bad[:8]:
            print(f"   {r['file']:24s} {r['ok']}/{r['total']} = {r['rate']:.0%}")
    else:
        print("\n✓ 全部文件溯源完整")
    print("\n说明：悬空多为**修复前采集的历史数据**。重新采集即可消除。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
