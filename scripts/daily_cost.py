"""端到端：这台家电每天花你多少钱？

从**采集数据**直接算，不手输参数。

用法:
  PYTHONPATH=src python3 scripts/daily_cost.py 冰箱
  PYTHONPATH=src python3 scripts/daily_cost.py --find "米家冰箱Pro 微冰鲜"
  PYTHONPATH=src python3 scripts/daily_cost.py --replace --old "米家冰箱 256L三门" \
      --new "米家冰箱Pro 微冰鲜系列"
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from goodsdex.appliance import (  # noqa: E402
    Appliance, Tariff, compare_replace, daily_cost,
    parse_energy_kwh, render_compare, render_cost,
)
from goodsdex.entities import effective_machines  # noqa: E402

CATS = ROOT / "data" / "categories"


def load_category(name: str) -> list[dict]:
    f = CATS / f"{name}.json"
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return []


def to_appliance(rec: dict) -> Appliance:
    """把一条采集记录转成 Appliance（字段各自溯源）"""
    p = rec.get("product") or {}
    v = (rec.get("view") or {}).get("values") or {}
    price = None
    for k in ("price", "pc_price"):
        if v.get(k) is not None:
            try:
                price = float(v[k])
                break
            except (TypeError, ValueError):
                pass
    energy = parse_energy_kwh(v.get("耗电量"))
    src = ""
    if energy is not None:
        src = "官方商品页「耗电量」参数"
    return Appliance(name=p.get("name") or "", price=price or 0.0,
                     energy=energy, category=p.get("category") or "",
                     energy_source=src)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("category", nargs="?", help="分类名，如 冰箱")
    ap.add_argument("--find", help="按关键词找一台")
    ap.add_argument("--lifespan", type=float, default=10.0, help="预期寿命（年，假设）")
    ap.add_argument("--replace", action="store_true", help="换新对比")
    ap.add_argument("--old", help="旧机名（关键词）")
    ap.add_argument("--new", help="新机名（关键词）")
    ap.add_argument("--old-age", type=float, default=0.0, help="旧机已用年数")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.replace:
        pool = [r for f in CATS.glob("*.json") for r in load_category(f.stem)]
        ms = effective_machines(pool, dedupe=True)
        old = _find_one(ms, a.old)
        new = _find_one(ms, a.new)
        if not old or not new:
            print(f"找不到：{'旧机' if not old else ''} {'新机' if not new else ''}")
            return 1
        res = compare_replace(to_appliance(old), to_appliance(new),
                              lifespan_years=a.lifespan, old_age_years=a.old_age)
        print(json.dumps(res, ensure_ascii=False, indent=1) if a.json
              else render_compare(res))
        return 0

    if a.find:
        pool = [r for f in CATS.glob("*.json") for r in load_category(f.stem)]
        rec = _find_one(effective_machines(pool, dedupe=True), a.find)
        if not rec:
            print(f"找不到「{a.find}」")
            return 1
        cb = daily_cost(to_appliance(rec), lifespan_years=a.lifespan)
        print(json.dumps(cb.to_dict(), ensure_ascii=False, indent=1) if a.json
              else render_cost(cb))
        return 0

    if not a.category:
        ap.print_help()
        return 1
    recs = effective_machines(load_category(a.category), dedupe=True)
    if not recs:
        print(f"分类「{a.category}」没有整机数据")
        return 1
    print(f"分类「{a.category}」整机 {len(recs)} 台 —— 日成本（电费+折旧）")
    print(f"假设：寿命 {a.lifespan:.0f} 年，电价 "
          f"{Tariff().blended} 元/度（{Tariff().source}）")
    print()
    rows = []
    for r in recs:
        cb = daily_cost(to_appliance(r), lifespan_years=a.lifespan)
        rows.append(cb)
    rows.sort(key=lambda c: -c.total_per_day)
    print(f"{'机型':30s} {'购机价':>8s} {'耗电':>12s} {'电费/天':>8s} "
          f"{'折旧/天':>8s} {'合计/天':>8s}")
    print("-" * 82)
    for cb in rows:
        e = f"{cb.energy_kwh_day}" if cb.energy_kwh_day is not None else "—"
        p = cb.depreciation_per_day * cb.lifespan_years * 365
        print(f"{cb.device[:28]:30s} {p:8.0f} {e:>12s} "
              f"{cb.electricity_per_day:8.2f} {cb.depreciation_per_day:8.2f} "
              f"{cb.total_per_day:8.2f}")
    return 0


def _find_one(recs: list[dict], kw: str | None) -> dict | None:
    if not kw:
        return None
    for r in recs:
        if kw.lower() in ((r.get("product") or {}).get("name") or "").lower():
            return r
    return None


if __name__ == "__main__":
    sys.exit(main())
