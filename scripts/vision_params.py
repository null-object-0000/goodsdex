"""视觉参数提取 CLI。

用法:
  PYTHONPATH=src python3 scripts/vision_params.py <图片URL或本地路径>
  PYTHONPATH=src python3 scripts/vision_params.py --category 壁挂空调 --limit 3
  PYTHONPATH=src python3 scripts/vision_params.py --category 壁挂空调 --limit 3 --write

--write 会把视觉断言合并进 data/categories/<分类>.json（新增，不覆盖接口数据）。
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from goodsdex.vision_extract import (SRC_VISION, extract_params_from_image,
                                     to_assertions)
from goodsdex.resolve import build_view, guess_category

CATS = ROOT / "data" / "categories"


def find_spec_images(rec: dict) -> list[dict]:
    """从一条记录里找「规格参数」tab 的图片（需要原始响应）"""
    out = []
    for c in rec.get("captures") or []:
        if c.get("source") != "mi_cn_pc":
            continue
        raw = c.get("response_raw") or ""
        try:
            j = json.loads(raw)
        except Exception:
            continue
        tabs = ((j.get("data") or {}).get("extend_info") or {}).get("desc_tabs_view") or []
        for ti, t in enumerate(tabs):
            if t.get("name") != "规格参数":
                continue
            for pi, blk in enumerate(t.get("tab_content") or []):
                img = ((blk.get("plain_view") or {}).get("img") or "")
                if img:
                    out.append({"url": img, "tab_index": ti, "part_index": pi})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", help="图片 URL 或本地路径")
    ap.add_argument("--category", help="对某分类批量抽取")
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--write", action="store_true", help="把视觉断言合并回分类文件")
    a = ap.parse_args()

    if a.category:
        fp = CATS / f"{a.category}.json"
        if not fp.exists():
            print(f"分类文件不存在: {fp}")
            return 1
        recs = json.loads(fp.read_text(encoding="utf-8"))
        machines = [r for r in recs if (r.get("product") or {}).get("kind") == "machine"]
        targets = machines[:a.limit]
        print(f"分类「{a.category}」整机 {len(machines)} 款，处理前 {len(targets)} 款\n")
        tmp = tempfile.mkdtemp(prefix="gd-vision-")
        for r in targets:
            name = r["product"]["name"]
            # 已有参数的跳过
            vals = (r.get("view") or {}).get("values") or {}
            if vals.get("_params_empty") is not True and len(vals) > 25:
                print(f"  跳过（接口已有参数）: {name[:36]}")
                continue
            imgs = find_spec_images(r)
            if not imgs:
                print(f"  无规格参数图: {name[:36]}")
                continue
            print(f"  {name[:36]}  规格图 {len(imgs)} 张")
            all_params, all_caps, all_asserts = {}, [], []
            t0 = time.time()
            for im in imgs:
                tgt = im["url"]
                if tgt.startswith("http"):
                    lp = Path(tmp) / f"{len(all_params)}_{im['part_index']}.jpg"
                    subprocess.run(["curl", "-sS", "-m", "40", "-o", str(lp), tgt],
                                   capture_output=True)
                    tgt = str(lp)
                res = extract_params_from_image(tgt, outdir=tmp)
                n = len(res["params"])
                print(f"     图{im['part_index']}: {n} 项"
                      + (f" 错误{len(res['errors'])}" if res["errors"] else ""))
                caps, asserts = to_assertions(im["url"], im["tab_index"],
                                              im["part_index"], res["params"],
                                              r["product"]["product_id"])
                all_caps += caps
                all_asserts += asserts
                all_params.update(res["params"])
            print(f"     合计 {len(all_params)} 项，用时 {time.time()-t0:.0f}s")

            if a.write and all_asserts:
                from goodsdex.facts import Assertion
                recs_a = [Assertion(**{k: v for k, v in x.items()
                                       if k in ("assertion_id", "subject_id", "capture_id",
                                                "source", "attribute", "raw_value", "locator",
                                                "ui_location", "page", "parser_version",
                                                "availability")})
                          for x in r["assertions"]]
                recs_a += all_asserts
                v = build_view(recs_a, category=guess_category(name),
                               subject_id=r["product"]["product_id"])
                r["assertions"] = [x.to_dict() for x in recs_a]
                r["captures"] = (r.get("captures") or []) + [c.to_dict() for c in all_caps]
                r["view"] = v.to_dict()
                r.setdefault("product", {})["vision_extracted"] = True
                print(f"     已合并 -> 视图值 {len(v.values)} 项")
        if a.write:
            tmpfp = fp.with_suffix(".json.tmp")
            tmpfp.write_text(json.dumps(recs, ensure_ascii=False, indent=1),
                             encoding="utf-8")
            tmpfp.replace(fp)
            print(f"\n-> {fp}")
        return 0

    if a.image:
        res = extract_params_from_image(a.image)
        print(json.dumps(res["params"], ensure_ascii=False, indent=1))
        if res["errors"]:
            print("错误:")
            for e in res["errors"]:
                print("  ", e)
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
