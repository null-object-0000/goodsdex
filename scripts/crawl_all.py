"""全量采集：遍历所有官方分类，落盘到 data/categories/<分类>.json

用法:
  PYTHONPATH=src python3 scripts/crawl_all.py            # 全部 84 类
  PYTHONPATH=src python3 scripts/crawl_all.py 手机 耳机    # 指定分类
  PYTHONPATH=src python3 scripts/crawl_all.py --resume    # 跳过已有非空结果

设计要点：
  - 每个分类独立落盘（中途失败不丢已完成的部分）
  - 分类之间串行、分类内部并发（避免对官方接口瞬时压力过大）
  - 进度写入 data/_progress.json，可断点续跑
  - 失败分类记录错误，不静默跳过
"""
from __future__ import annotations
import argparse
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from goodsdex.sources import mi_cn
from goodsdex import pipeline

OUT = ROOT / "data" / "categories"
PROGRESS = ROOT / "data" / "_progress.json"


def load_progress() -> dict:
    if PROGRESS.exists():
        try:
            return json.loads(PROGRESS.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_progress(p: dict) -> None:
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    tmp = PROGRESS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(PROGRESS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("categories", nargs="*", help="分类名（默认全部）")
    ap.add_argument("--resume", action="store_true", help="跳过已成功采集的分类")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--pause", type=float, default=2.0, help="分类之间的停顿秒数（防限流）")
    ap.add_argument("--max-pages", type=int, default=20)
    ap.add_argument("--only-missing", action="store_true", help="只跑上次失败的分类")
    a = ap.parse_args()

    allcats = mi_cn.list_categories()
    targets = a.categories or list(allcats.keys())

    OUT.mkdir(parents=True, exist_ok=True)
    prog = load_progress()
    if a.only_missing:
        targets = [c for c in targets if prog.get(c, {}).get("status") != "ok"]
    elif a.resume:
        targets = [c for c in targets
                   if prog.get(c, {}).get("status") != "ok"
                   or not (OUT / f"{pipeline.safe_filename(c)}.json").exists()]

    print(f"目标 {len(targets)}/{len(allcats)} 个分类", flush=True)
    t_start = time.time()
    for i, cat in enumerate(targets, 1):
        t0 = time.time()
        try:
            recs = pipeline.run_category(cat, limit=0, max_pages=a.max_pages,
                                         workers=a.workers, outdir=OUT, verbose=False)
            n = len(recs)
            # 统计质量指标
            nprod_ok = sum(1 for r in recs
                           if r["product"].get("identity_confidence") == "verified")
            assert_ok = sum(1 for r in recs
                            if all(c["status"] == "success" for c in r["captures"]))
            prog[cat] = {"status": "ok", "products": n, "identity_ok": nprod_ok,
                         "capture_ok": assert_ok, "seconds": round(time.time() - t0, 1)}
            print(f"[{i}/{len(targets)}] ✓ {cat:18s} {n:4d} 款 "
                  f"({time.time()-t0:.0f}s)", flush=True)
        except Exception as e:
            prog[cat] = {"status": "error", "error": f"{type(e).__name__}: {e}",
                         "seconds": round(time.time() - t0, 1)}
            print(f"[{i}/{len(targets)}] ✗ {cat:18s} {type(e).__name__}: {e}", flush=True)
            traceback.print_exc(limit=2)
        save_progress(prog)
        if i < len(targets):
            time.sleep(a.pause)   # 分类之间停顿，避免触发官方限流

    ok = sum(1 for v in prog.values() if v.get("status") == "ok")
    err = [k for k, v in prog.items() if v.get("status") == "error"]
    total = sum(v.get("products", 0) for v in prog.values())
    print(f"\n完成：{ok} 类成功，{len(err)} 类失败，累计 {total} 款商品"
          f"，用时 {time.time()-t_start:.0f}s")
    if err:
        print(f"失败分类：{', '.join(err)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
