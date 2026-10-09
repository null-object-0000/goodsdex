"""跨品类基准：OCR vs 视觉 LLM（用接口参数当基准）

用法:
  PYTHONPATH=src:scripts python3 scripts/bench_ocr_vision.py --limit 6
  PYTHONPATH=src:scripts python3 scripts/bench_ocr_vision.py --limit 6 --report
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bench_common import evaluate
from ocr_compare import baidu_token, load_keys, ocr_general
from ocr_position import ocr_with_location, pair_by_position
from vision_params import find_spec_images
from vision_params_lib import META_FIELDS, count_real_params

CATS = ROOT / "data" / "categories"
OUT = ROOT / "data" / "_bench_ocr_vision.json"
TMP = Path("/tmp/gd-bench")


def baseline_params(rec: dict) -> dict:
    """接口参数作为基准（只取非元数据、非视觉的）"""
    out = {}
    for a in rec.get("assertions") or []:
        if a.get("source") == "mi_cn_pc_vision":
            continue
        k = a.get("attribute", "")
        if k in META_FIELDS or k.startswith("_"):
            continue
        out.setdefault(k, a.get("raw_value"))
    return out


def download(url: str, fp: Path) -> bool:
    TMP.mkdir(parents=True, exist_ok=True)
    if fp.exists() and fp.stat().st_size > 0:
        return True
    subprocess.run(["curl", "-sS", "-m", "40", "-o", str(fp), url],
                   capture_output=True)
    return fp.exists() and fp.stat().st_size > 0


def run_one(rec: dict, cat: str, token: str, tmp: Path) -> dict:
    name = rec["product"]["name"]
    base = baseline_params(rec)
    imgs = find_spec_images(rec)
    if not base or not imgs:
        return {}
    # 选图：优先"像规格表"的那张（用零成本预筛），而不是无脑取第一张 ——
    # 实测教训：imgs[0] 常是商品详情图而非规格参数图，会导致两边都提取失败。
    from img_preselect import download as _dl, looks_like_spec, profile_image
    im, best = None, None
    for cand in imgs[:12]:
        lp = tmp / f"{hashlib.md5(cand['url'].encode()).hexdigest()[:16]}.jpg"
        if not download(cand["url"], lp):
            continue
        pr = profile_image(str(lp))
        if looks_like_spec(pr):
            im = cand
            break
        if best is None or pr.aspect > best[1].aspect:
            best = (cand, pr)
    if im is None and best is not None:
        im, _ = best          # 没有像规格表的，退回长宽比最大的
    if im is None:
        return {}
    # 复用循环里已下载的图（im 对应文件已在 tmp 下）
    fp = tmp / f"{hashlib.md5(im['url'].encode()).hexdigest()[:16]}.jpg"
    if not fp.exists():
        if not download(im["url"], fp):
            return {}
    row = {"category": cat, "product": name, "image": str(fp),
           "baseline_n": len(base), "results": {}}
    try:
        items = ocr_with_location(str(fp), token)
        pairs = pair_by_position(items)
        row["results"]["ocr"] = evaluate(base, pairs, "OCR")
    except Exception as e:
        row["results"]["ocr"] = {"label": "OCR", "error": f"{type(e).__name__}: {e}",
                                 "recall": 0, "precision": 0, "baseline_n": len(base),
                                 "got_n": 0, "hits": [], "misses": [], "extras": []}
    try:
        from goodsdex.vision_extract import extract_params_from_image
        vr = extract_params_from_image(str(fp))
        row["results"]["vision"] = evaluate(base, vr["params"], "视觉LLM")
    except Exception as e:
        row["results"]["vision"] = {"label": "视觉LLM", "error": f"{type(e).__name__}: {e}",
                                    "recall": 0, "precision": 0, "baseline_n": len(base),
                                    "got_n": 0, "hits": [], "misses": [], "extras": []}
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=6, help="每个品类取几台")
    ap.add_argument("--max-total", type=int, default=20)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    # 按品类均衡取样（避免手机淹没其他品类）
    bycat: dict[str, list] = {}
    for f in sorted(CATS.glob("*.json")):
        cat = f.stem
        for r in json.loads(f.read_text(encoding="utf-8")):
            if (r.get("product") or {}).get("kind") != "machine":
                continue
            if count_real_params(r) < 8:
                continue
            if not find_spec_images(r):
                continue
            bycat.setdefault(cat, []).append(r)

    targets = []
    for cat, rs in sorted(bycat.items(), key=lambda x: -len(x[1])):
        targets += [(cat, r) for r in rs[:a.limit]]
    targets = targets[:a.max_total]

    print(f"目标 {len(targets)} 台，覆盖 {len({c for c,_ in targets})} 个品类\n")
    token = baidu_token(load_keys())
    rows = []
    t0 = time.time()
    for i, (cat, r) in enumerate(targets, 1):
        try:
            row = run_one(r, cat, token, TMP)
        except Exception as e:
            print(f"[{i}/{len(targets)}] ✗ {cat} {type(e).__name__}: {e}")
            continue
        if not row:
            continue
        o, v = row["results"]["ocr"], row["results"]["vision"]
        rows.append(row)
        print(f"[{i}/{len(targets)}] {cat[:10]:12s} {row['product'][:22]:24s} "
              f"基准{row['baseline_n']:2d} | "
              f"OCR {o.get('recall',0):.0%}/{o.get('precision',0):.0%} "
              f"视觉 {v.get('recall',0):.0%}/{v.get('precision',0):.0%}")
        OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    if not rows:
        print("无有效样本")
        return 1

    print(f"\n用时 {time.time()-t0:.0f}s，样本 {len(rows)}")
    for m in ("ocr", "vision"):
        rs = [r["results"][m] for r in rows if "error" not in r["results"][m]]
        if not rs:
            continue
        rec = sum(x["recall"] for x in rs) / len(rs)
        pre = sum(x["precision"] for x in rs) / len(rs)
        print(f"  {m:8s} 平均召回 {rec:.0%}  平均精度 {pre:.0%}  (n={len(rs)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
