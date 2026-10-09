"""批量路由验证：跨品类取样，看 OCR/视觉 分流是否合理。

评估方式（不依赖我手敲的标准答案）：
  - 对每张图，跑 OCR 与视觉两条路
  - 用「视觉结果」当参照，算 OCR 命中率（视觉在非表格图上明显更稳）
  - 同时记录路由决策，看决策与"实际谁更好"是否一致

用法:
  PYTHONPATH=src:scripts python3 scripts/bench_route.py --per-cat 2
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from layout_detect import contamination, layout_features, route
from ocr_compare import load_keys, baidu_token
from ocr_position import ocr_with_location, pair_by_position
from vision_params import find_spec_images, NON_SPEC_TAB
from vision_params_lib import count_real_params

CATS = ROOT / "data" / "categories"
TMP = Path("/tmp/gd-route")
OUT = ROOT / "data" / "_bench_route.json"


def nk(s):
    import unicodedata
    s = unicodedata.normalize("NFKC", str(s or ""))
    return re.sub(r"[\s（）()★*\-]", "", s).lower()


def hit_rate(ref: dict, got: dict) -> dict:
    """got 相对 ref(视觉结果) 的键命中率与值一致率"""
    if not ref:
        return {"key_hit": 0.0, "val_ok": 0.0, "n_ref": 0}
    kh = vo = 0
    for rk, rv in ref.items():
        m = next((gk for gk in got if nk(rk) == nk(gk) or
                  (len(nk(rk)) >= 3 and nk(rk) in nk(gk)) or
                  (len(nk(gk)) >= 3 and nk(gk) in nk(rk))), None)
        if m is None:
            continue
        kh += 1
        if nk(rv)[:6] and nk(rv)[:6] in nk(got[m]):
            vo += 1
    n = len(ref)
    return {"key_hit": round(kh / n, 3), "val_ok": round(vo / n, 3), "n_ref": n}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cat", type=int, default=2)
    ap.add_argument("--max-total", type=int, default=12)
    a = ap.parse_args()

    TMP.mkdir(parents=True, exist_ok=True)
    # 取样：优先有"型号命名 tab"的商品（更可能是真规格表）
    picked = []
    for f in sorted(CATS.glob("*.json")):
        cat = f.stem
        n = 0
        for r in json.loads(f.read_text(encoding="utf-8")):
            if (r.get("product") or {}).get("kind") != "machine":
                continue
            if count_real_params(r) < 8:
                continue
            imgs = [i for i in find_spec_images(r)
                    if i.get("tab_name") and not NON_SPEC_TAB.search(i["tab_name"])]
            if not imgs:
                continue
            picked.append((cat, r["product"]["name"], imgs[0]["url"],
                           imgs[0]["tab_name"]))
            n += 1
            if n >= a.per_cat:
                break
        if len(picked) >= a.max_total:
            break
    picked = picked[:a.max_total]

    token = baidu_token(load_keys())
    from goodsdex.vision_extract import extract_params_from_image

    rows = []
    print(f"{'品类':12s}{'商品':22s}{'块':>4s}{'配对':>5s}{'污染':>6s}"
          f"{'路由':>7s}{'OCR命中':>8s}{'视觉项':>7s}")
    for cat, name, url, tab in picked:
        fp = TMP / f"{hashlib.md5(url.encode()).hexdigest()[:16]}.jpg"
        if not fp.exists():
            subprocess.run(["curl", "-sS", "-m", "40", "-o", str(fp), url],
                           capture_output=True)
        if not fp.exists() or fp.stat().st_size == 0:
            continue
        try:
            items = ocr_with_location(str(fp), token)
            pairs = pair_by_position(items)
            f = layout_features(items)
            c = contamination(pairs)
            rt, why = route(f, pairs, c["rate"])
            vis = extract_params_from_image(str(fp), ocr="off")
        except Exception as e:
            print(f"{cat[:10]:12s}{name[:20]:22s}  ✗ {type(e).__name__}: {e}")
            continue
        hr = hit_rate(vis["params"], pairs)
        row = {"category": cat, "product": name, "tab": tab, "image": str(fp),
               "blocks": f.get("n"), "pairs": len(pairs),
               "contamination": c["rate"], "route": rt, "reason": why,
               "ocr_vs_vision": hr, "vision_n": len(vis["params"]),
               "ocr_params": pairs, "vision_params": vis["params"]}
        rows.append(row)
        print(f"{cat[:10]:12s}{name[:20]:22s}{f.get('n',0):>4d}{len(pairs):>5d}"
              f"{c['rate']:>6.0%}{rt:>7s}{hr['key_hit']:>8.0%}{len(vis['params']):>7d}")

    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    if rows:
        ocr_ok = [r for r in rows if r["route"] == "ocr"]
        vis_ok = [r for r in rows if r["route"] == "vision"]
        print(f"\n样本 {len(rows)}")
        print(f"  路由到 OCR   {len(ocr_ok)} 张，其中 OCR 键命中率 "
              f"{sum(r['ocr_vs_vision']['key_hit'] for r in ocr_ok)/max(len(ocr_ok),1):.0%}")
        print(f"  路由到 视觉  {len(vis_ok)} 张")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
