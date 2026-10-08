"""采集主流程：分类 -> 枚举 -> 多源采集(断言) -> 解析视图 -> 输出

三层（不丢证据）：
  Capture     原响应 + 状态（证据）
  Assertion   谁对哪个属性声明了什么
  View        按策略选出的展示值（可重建）

用法:
  python3 -m goodsdex.pipeline --list-categories
  python3 -m goodsdex.pipeline --category 吹风机
  python3 -m goodsdex.pipeline --pid 23966
"""
from __future__ import annotations
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .facts import Bundle, Capture, CaptureStatus, Subject
from .identity import build_identity
from .kind import classify_product_kind
from .resolve import build_view, guess_category
from .sources import mi_cn

# 已接入的数据源（--sources 只接受这些；未知源直接报错，不静默跳过）
SUPPORTED_SOURCES = {"mi_cn"}

DEFAULT_OUT = Path("data")
# 原响应体积上限（避免单个商品把数据文件撑爆）
RAW_SNAPSHOT_LIMIT = 300_000


def _trim_raw(raw: str) -> str:
    if len(raw) <= RAW_SNAPSHOT_LIMIT:
        return raw
    half = RAW_SNAPSHOT_LIMIT // 2
    return raw[:half] + f"\n...<省略 {len(raw) - RAW_SNAPSHOT_LIMIT} 字节>...\n" + raw[-half:]


def collect_one(pid: str, name_hint: str = "", category: str = "",
                discovery: dict | None = None, variants: list | None = None) -> dict:
    """采集单个商品（产品级），返回含身份、证据、断言、视图的记录"""
    variants = variants or []
    prod = build_identity(pid, variants, market="CN", source="mi_cn",
                          category=category or "")
    if not prod.name:
        prod.name = name_hint

    bundle = Bundle(subject=Subject(subject_id=prod.product_id, kind="product",
                                    name=prod.name, market="CN",
                                    external_ids=prod.external_ids),
                    discovery=discovery or {})

    for fn in (mi_cn.fetch_mobile, mi_cn.fetch_pc):
        try:
            caps, assertions = fn(pid)
        except Exception as e:
            # 采集异常 -> 独立状态，不伪装成字段
            bundle.add_capture(Capture.make(
                "mi_cn", f"unknown://{fn.__name__}", "",
                status=CaptureStatus.TRANSPORT_ERROR, error=f"{type(e).__name__}: {e}"))
            continue
        for c in caps:
            c.response_raw = _trim_raw(c.response_raw)
            bundle.add_capture(c)
        bundle.add_assertions(assertions)

    # subject 名称以官方产品名为准
    for a in bundle.assertions:
        if a.attribute == "name" and a.raw_value:
            bundle.subject.name = str(a.raw_value)
            break

    cat = category or guess_category(bundle.subject.name)
    prod.category = prod.category or cat
    # 类型分流：整机 vs 配件耗材 vs 服务（服务/耗材没有换代意义，不进代际表）
    prod_kind = classify_product_kind(bundle.subject.name, cat)
    view = build_view(bundle.assertions, category=cat,
                      subject_id=bundle.subject.subject_id)

    # 变体级：价格与可购买属性挂在变体上（价格是时间序列，不是产品永久属性）
    price_observations = []
    for v in prod.variants:
        if v.external_ids.get("mi_cn.commodity_id"):
            price_observations.append({
                "variant_id": v.variant_id, "name": v.name,
                "attrs": v.attrs,
                "external_ids": v.external_ids,
            })

    pd = prod.to_dict()
    pd["kind"] = prod_kind
    return {"product": pd,
            "captures": [c.to_dict() for c in bundle.captures],
            "assertions": [a.to_dict() for a in bundle.assertions],
            "view": view.to_dict(),
            "market_prices": price_observations,
            "discovery": bundle.discovery,
            "fetched_at": bundle.fetched_at}


def _summary(rec: dict) -> str:
    caps = rec["captures"]
    ok = sum(1 for c in caps if c["status"] == "success")
    bad = [c for c in caps if c["status"] not in ("success", "partial")]
    v = rec["view"]
    name = rec["product"].get("name") or "?"
    nvar = len(rec["product"].get("variants") or [])
    rej = f" 异常{len(bad)}" if bad else ""
    return (f"  {'✓' if ok else '✗'} {name[:24]:26s} 变体={nvar:<2d} "
            f"断言={len(rec['assertions']):3d} 视图值={len(v['values']):3d} "
            f"关系={len(v['relations']):2d} 缺口={len(v['gaps']):2d} "
            f"[{ok}/{len(caps)}源]{rej}")


def run_category(category: str, limit: int = 0, max_pages: int = 20,
                 workers: int = 4, outdir: Path = DEFAULT_OUT,
                 verbose: bool = True) -> list[dict]:
    cats = mi_cn.list_categories()
    kw = cats.get(category, category)
    if verbose:
        print(f"[1/3] 分类「{category}」-> 关键词「{kw}」")
    enum = mi_cn.enumerate_products(kw, max_pages=max_pages)
    prods, discovery = enum["items"], enum["discovery"]
    if limit:
        prods = prods[:limit]
    if verbose:
        print(f"      发现 {len(prods)} 个商品 | total={discovery['total_reported']} "
              f"完整性={discovery['completeness']} ({discovery['stop_reason']})")
        print("[2/3] 采集（断言层，保留原响应）")

    out: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(collect_one, p["pid"], p["name"], category, discovery,
                          p.get("variants")): p for p in prods}
        for f in as_completed(futs):
            p = futs[f]
            try:
                rec = f.result()
            except Exception as e:
                if verbose:
                    print(f"  ✗ {p['name'][:30]} {type(e).__name__}: {e}")
                continue
            out.append(rec)

    # 稳定排序（并发完成顺序不确定，输出必须可复现）
    out.sort(key=lambda r: r["product"]["product_id"])
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"{category}.json"
    tmp = fp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(fp)          # 原子替换，避免写一半崩掉
    if verbose:
        for r in out:
            print(_summary(r))
        print(f"\n[3/3] {len(out)} 款 -> {fp}")
        print(f"      发现: {json.dumps(discovery, ensure_ascii=False)}")
    return out


def run_pid(pid: str, outdir: Path = DEFAULT_OUT) -> dict:
    rec = collect_one(pid)
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"pid_{pid}.json"
    tmp = fp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(fp)
    v = rec["view"]
    print(f"{rec['product'].get('name')} | 断言 {len(rec['assertions'])} | "
          f"视图值 {len(v['values'])} | 关系 {len(v['relations'])} | 缺口 {len(v['gaps'])}")
    print(f"-> {fp}")
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(prog="goodsdex.pipeline", description="商品数据采集流程")
    ap.add_argument("--list-categories", action="store_true", help="列出可采集分类")
    ap.add_argument("--category", help="分类名（或直接给关键词）")
    ap.add_argument("--pid", help="单个商品 ID")
    ap.add_argument("--sources", default="mi_cn", help="数据源。当前已接入：mi_cn")
    ap.add_argument("--limit", type=int, default=0, help="限制商品数")
    ap.add_argument("--max-pages", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)

    srcs = tuple(s.strip() for s in a.sources.split(",") if s.strip())
    unknown = [s for s in srcs if s not in SUPPORTED_SOURCES]
    if unknown:
        ap.error(f"未接入的数据源: {', '.join(unknown)}。"
                 f"当前支持: {', '.join(sorted(SUPPORTED_SOURCES))}")

    if a.list_categories:
        cats = mi_cn.list_categories()
        print(f"官方分类 {len(cats)} 个：")
        for n, k in cats.items():
            print(f"  {n:24s} -> {k}")
        return 0
    if a.pid:
        run_pid(a.pid, Path(a.out))
        return 0
    if not a.category:
        ap.print_help()
        return 1
    run_category(a.category, a.limit, a.max_pages, a.workers, Path(a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
