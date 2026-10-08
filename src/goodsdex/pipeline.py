"""采集主流程：分类 -> 枚举 -> 多源 -> 归一化 -> 输出

用法:
  python3 -m goodsdex.pipeline --list-categories
  python3 -m goodsdex.pipeline --category 吹风机
  python3 -m goodsdex.pipeline --category 耳机 --sources mi_cn --limit 5
  python3 -m goodsdex.pipeline --pid 23966          # 单个商品
"""
from __future__ import annotations
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .model import Record, SOURCE_META, now_iso
from .normalize import normalize_record
from .sources import mi_cn

DEFAULT_OUT = Path("data")


def collect_one(pid: str, name_hint: str = "", sources=("mi_cn",),
                category: str = "") -> Record:
    """采集单个商品"""
    rec = Record(key=pid, name=name_hint, category=category)
    rec.source_urls["mi_cn_pc"] = f"https://www.mi.com/shop/buy/detail?product_id={pid}"
    rec.source_urls["mi_cn_mobile"] = f"https://m.mi.com/commodity/detail/{pid}"

    if "mi_cn" in sources:
        raw = {}
        try:
            raw.update(mi_cn.fetch_mobile(pid) or {})
            rec.sources_used.append("mi_cn_mobile")
        except Exception as e:
            rec.data["_mobile_err"] = str(e)
        try:
            raw.update(mi_cn.fetch_pc(pid) or {})
            rec.sources_used.append("mi_cn_pc")
        except Exception as e:
            rec.data["_pc_err"] = str(e)
        for k, (v, p) in raw.items():
            rec.set(k, v, p)

    # 归一化（展开嵌套参数、别名合并、冲突检测）
    norm = normalize_record({"data": rec.data, "provenance": rec.provenance})
    rec.data = norm["data"]
    rec.provenance = norm["provenance"]
    rec.conflicts = norm["conflicts"]
    rec.dropped = norm["dropped"]
    if not rec.name:
        rec.name = str(rec.data.get("name") or name_hint)
    return rec


def run_category(category: str, sources=("mi_cn",), limit: int = 0,
                 max_pages: int = 20, workers: int = 4, outdir: Path = DEFAULT_OUT,
                 verbose: bool = True) -> list[Record]:
    cats = mi_cn.list_categories()
    kw = cats.get(category, category)
    if verbose:
        print(f"[1/3] 分类「{category}」-> 关键词「{kw}」")
    prods = mi_cn.enumerate_products(kw, max_pages=max_pages)
    if limit:
        prods = prods[:limit]
    if verbose:
        print(f"      枚举到 {len(prods)} 个商品\n[2/3] 多源采集")

    out: list[Record] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(collect_one, p["pid"], p["name"], sources, category): p
                for p in prods}
        for f in as_completed(futs):
            p = futs[f]
            try:
                rec = f.result()
            except Exception as e:
                if verbose:
                    print(f"  ✗ {p['name'][:30]} {e}")
                continue
            out.append(rec)
            if verbose:
                print(f"  ✓ {rec.name[:26]:28s} 字段={len(rec.data):3d} "
                      f"源={','.join(rec.sources_used)} 冲突={len(rec.conflicts)}")

    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"{category}.json"
    fp.write_text(json.dumps([r.to_dict() for r in out], ensure_ascii=False, indent=1),
                  encoding="utf-8")
    if verbose:
        print(f"\n[3/3] {len(out)} 款 -> {fp}")
        tot_c = sum(len(r.conflicts) for r in out)
        tot_f = sum(len(r.data) for r in out)
        print(f"      字段总数 {tot_f} | 冲突 {tot_c}")
    return out


def run_pid(pid: str, sources=("mi_cn",), outdir: Path = DEFAULT_OUT) -> Record:
    rec = collect_one(pid, sources=sources)
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"pid_{pid}.json"
    fp.write_text(json.dumps(rec.to_dict(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{rec.name} | 字段 {len(rec.data)} | 冲突 {len(rec.conflicts)} -> {fp}")
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(prog="goodsdex.pipeline", description="商品数据采集流程")
    ap.add_argument("--list-categories", action="store_true", help="列出可采集分类")
    ap.add_argument("--category", help="分类名（或直接给关键词）")
    ap.add_argument("--pid", help="单个商品 ID")
    ap.add_argument("--sources", default="mi_cn", help="数据源，逗号分隔（mi_cn,baike,zol）")
    ap.add_argument("--limit", type=int, default=0, help="限制商品数")
    ap.add_argument("--max-pages", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)

    srcs = tuple(s.strip() for s in a.sources.split(",") if s.strip())

    if a.list_categories:
        cats = mi_cn.list_categories()
        print(f"官方分类 {len(cats)} 个：")
        for n, k in cats.items():
            print(f"  {n:24s} -> {k}")
        return 0
    if a.pid:
        run_pid(a.pid, srcs, Path(a.out))
        return 0
    if not a.category:
        ap.print_help()
        return 1
    run_category(a.category, srcs, a.limit, a.max_pages, a.workers, Path(a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
