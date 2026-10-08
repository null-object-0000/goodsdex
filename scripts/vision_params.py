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
import re
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


# 非参数 tab（服务条款/安装须知等，不含规格）
NON_SPEC_TAB = re.compile(r"售后|服务条款|安装须知|安装费用|保障|说明|政策|常见问题|推荐|评价")


def find_spec_images(rec: dict) -> list[dict]:
    """从一条记录里找**规格参数图**。

    实测发现：家电品类的 tab 命名没有统一规范 ——
      空调: '规格参数'
      冰箱: '256L(星锻银)' / '微冰鲜-十字门' / '十字-513L'（按型号命名的 tab）
    所以不能只匹配"规格参数"这个名字。

    策略：取所有**非服务类** tab 的图片（服务条款/安装须知等排除），
    由视觉提取去判断内容是不是参数表。
    """
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
            nm = t.get("name") or ""
            if NON_SPEC_TAB.search(nm):
                continue
            for pi, blk in enumerate(t.get("tab_content") or []):
                img = ((blk.get("plain_view") or {}).get("img") or "")
                if img:
                    out.append({"url": img, "tab_index": ti, "part_index": pi,
                                "tab_name": nm})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", help="图片 URL 或本地路径")
    ap.add_argument("--category", help="对某分类批量抽取")
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--write", action="store_true", help="把视觉断言合并回分类文件")
    ap.add_argument("--min-keep", type=int, default=2, help="每台至少保留几张候选图")
    ap.add_argument("--max-keep", type=int, default=10, help="每台最多保留几张候选图")
    ap.add_argument("--per-tab", type=int, default=2, help="每个 tab 最多保留几张")
    ap.add_argument("--min-params", type=int, default=8,
                    help="接口已有多少项参数就跳过（默认 8）")
    ap.add_argument("--no-preselect", action="store_true",
                    help="不做预筛（成本高，仅在排查时用）")
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
            # 跳过条件必须看**真实参数数**，不是视图值总数 ——
            # 实测教训：视图值 25-44 主要是元数据（图片/评价/问答），
            # 用它当阈值会把 12 台需要视觉提取的冰箱误判为"已有参数"。
            from vision_params_lib import count_real_params
            nparam = count_real_params(r)
            if nparam >= a.min_params:
                print(f"  跳过（接口已有 {nparam} 项参数）: {name[:36]}")
                continue
            imgs = find_spec_images(r)
            if not imgs:
                print(f"  无规格参数图: {name[:36]}")
                continue
            # 零成本预筛：不做这步会按 100 张/台全量调视觉（实测冰箱），
            # 成本高 20 倍。预筛只减少候选，不判定。
            if not a.no_preselect:
                from img_preselect import preselect
                keep, pst = preselect(imgs, str(Path(tmp) / "pre"),
                                      min_keep=a.min_keep, max_keep=a.max_keep,
                                      per_tab=a.per_tab)
                print(f"  {name[:36]}  规格图 {pst['unique']} 张 -> 预筛保留 {pst['kept']} 张"
                      f"（筛掉 {pst['dropped']}）")
                imgs = keep
            else:
                print(f"  {name[:36]}  规格图 {len(imgs)} 张（未预筛）")
            all_params, all_caps, all_asserts = {}, [], []
            t0 = time.time()
            for im in imgs:
                tgt = im.get("local") or im["url"]
                res = extract_params_from_image(tgt, outdir=tmp)
                n = len(res["params"])
                print(f"     图{im['part_index']}: {n} 项"
                      + (f" 错误{len(res['errors'])}" if res["errors"] else ""))
                caps, asserts = to_assertions(im["url"], im["tab_index"],
                                              im["part_index"], res["params"],
                                              r["product"]["product_id"],
                                              aliases=res.get("aliases"))
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
