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


# 非参数 tab（服务/详情/营销类，不含规格）
NON_SPEC_TAB = re.compile(
    r"售后|服务条款|安装须知|安装费用|保障|说明|政策|常见问题|推荐|评价|"
    r"商品详情|产品详情|^详情|详情$|图文|介绍|晒单|开箱|安装|"
    r"包装清单|附件清单|清单")

# 通用 tab 名（不是型号，也不是参数页）—— 排除以免误当型号 tab
GENERIC_TAB = re.compile(
    r"^(商品详情|产品详情|详情|介绍|图文详情|包装清单|常见问题|"
    r"售后|服务|保障|政策|说明|用户评价|推荐)+$")

# 真正的型号 tab 特征（**白名单**，不是排除法）
# 实测教训：用"非通用名即为型号"的排除法，会把显示器规格描述
# （"27英寸 4K Type-C接口"、"1080P 144Hz"、"4K 60Hz Type-C版"）
# 当成型号名 —— 而且同一款会有多种表述，导致重复条目。
MODEL_TAB = re.compile(
    r"\d+\s*[L升]\b|\d+L\b"          # 容量：256L / 513L / 10kg
    r"|\d+\s*kg"                      # 重量：10kg
    r"|匹"                            # 空调匹数
    r"|(十字|法式|对开|三门|两门)(门)?$"  # 冰箱门体
    r"|(风冷|直冷|变频|定频)款"        # 洗衣机/冰箱 款式
    r"|^\d+GB|\d+GB\+"               # 手机容量
    r"|Pro|Max|Plus|Ultra")          # 型号后缀

# 名副其实的参数 tab（白名单，实测有规律）
SPEC_TAB = re.compile(r"参数|规格|specification")


def find_spec_images(rec: dict) -> list[dict]:
    """从一条记录里找**规格参数图**。

    实测教训（重要，曾导致系统性错误）：
      最初用"排除服务类 tab"的排除法，结果全库 23197 张候选图里
      **16516 张（71%）来自 tab='商品详情'** —— 那是营销图。
      后果：把「全面升级」「10年免费包修」这类宣传文案当成了产品参数。

    正确策略是**白名单优先 + 分层**：
      ① 名字含"参数/规格"的 tab（产品参数/商品参数/规格参数/参数页/参数）
         —— 名副其实，实测 1621 张
      ② tab 名是**具体型号**的（"256L(星锻银)"、"直冷-186L"）
         —— 家电按型号分栏，参数在各型号 tab 内
      ③ 其余（商品详情等营销 tab）**不取** —— 宁可漏，不可混入伪参数

    返回项带 tier 字段标明来源层级，便于事后按层级评估可信度。
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
            nm = (t.get("name") or "").strip()
            # ③ 服务/营销类直接排除
            if NON_SPEC_TAB.search(nm):
                continue
            if SPEC_TAB.search(nm):
                tier = 1                      # ① 名副其实的参数 tab
            elif MODEL_TAB.search(nm) and not GENERIC_TAB.search(nm):
                tier = 2                      # ② 型号 tab（白名单特征）
            else:
                continue                      # ③ 其余不取
            for pi, blk in enumerate(t.get("tab_content") or []):
                img = ((blk.get("plain_view") or {}).get("img") or "")
                if img:
                    out.append({"url": img, "tab_index": ti, "part_index": pi,
                                "tab_name": nm, "tier": tier})
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
        # 统一口径：排除已被形态过滤与已拆父记录（否则父记录也会被当作待补对象）
        from goodsdex.entities import effective_machines
        machines = effective_machines(recs)
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
