"""三种模式对照：纯视觉 / 混合(OCR+视觉) / 纯OCR

评估方式（吸取上一版教训）：
  - **不用手敲的 ground truth**（那测的是我）
  - 改为多维度客观指标：
      * 提取项数（越多说明覆盖越好，但可能虚构）
      * 键名规范度（是否落入已知品类属性词表）
      * 值完整度（是否含单位/数值齐整）
      * 三模式的**一致性**（互相印证 = 可信；分歧 = 需复核）
  - 原始输出全部落盘，可人工抽查

用法:
  PYTHONPATH=src:scripts python3 scripts/bench_modes.py /tmp/gd/spec_0.jpg /tmp/gd/spec_1.jpg
"""
from __future__ import annotations
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "data" / "_bench_modes.json"


def quality(params: dict, known_attrs: set) -> dict:
    """客观质量指标（不需要人工标准答案）"""
    if not params:
        return {"n": 0, "known_ratio": 0.0, "has_unit_ratio": 0.0,
                "suspicious": 0}
    known = sum(1 for k in params if k in known_attrs)
    # 值里含数字或单位 -> 像真参数
    unit = sum(1 for v in params.values()
               if re.search(r"\d|\u6beb\u7c73|mm|cm|L|W|dB|h|min|匹|级", str(v)))
    # 可疑：键太长 / 值是整段文字（>60字） / 键含标点
    susp = sum(1 for k, v in params.items()
               if len(str(k)) > 30 or len(str(v)) > 60 or re.search(r"[。；]", str(k)))
    return {"n": len(params),
            "known_ratio": round(known / len(params), 3),
            "has_unit_ratio": round(unit / len(params), 3),
            "suspicious": susp}


def consensus(a: dict, b: dict, c: dict) -> dict:
    """三种模式的一致性：至少两方一致的值"""
    allkeys = set(a) | set(b) | set(c)
    agree, disagree, only_one = 0, [], []
    for k in allkeys:
        vals = [d[k] for d in (a, b, c) if k in d]
        norm = {re.sub(r"\s", "", str(v)).lower() for v in vals}
        if len(norm) == 1 and len(vals) >= 2:
            agree += 1
        elif len(norm) > 1:
            disagree.append((k, vals))
        else:
            only_one.append(k)
    return {"total_keys": len(allkeys), "agree": agree,
            "disagree": len(disagree), "single_source": len(only_one),
            "disagree_detail": disagree[:6]}


def main() -> int:
    imgs = sys.argv[1:]
    if not imgs:
        print("用法: bench_modes.py <图片> [图片...]")
        return 1

    from goodsdex.vision_extract import (extract_params_from_image,
                                         _baidu_ocr_lines)
    from goodsdex.resolve import CATEGORY_RULES
    from goodsdex.vision_normalize import canonicalize_params
    from ocr_compare import load_keys, baidu_token
    from ocr_position import ocr_with_location, pair_by_position

    known = set()
    for rule in CATEGORY_RULES.values():
        for d in rule.get("attrs", []):
            known.add(d.attr_id)
            known.add(d.label)
    known |= set(list(AREA_HINTS))

    token = baidu_token(load_keys())
    rows = []
    for img in imgs:
        if not os.path.exists(img):
            print(f"跳过（不存在）: {img}")
            continue
        t0 = time.time()
        r_off = extract_params_from_image(img, ocr="off")
        t_off = time.time() - t0
        t0 = time.time()
        r_hyb = extract_params_from_image(img, ocr="hybrid")
        t_hyb = time.time() - t0
        t0 = time.time()
        items = ocr_with_location(img, token)
        ocr_pairs = pair_by_position(items)
        t_ocr = time.time() - t0

        row = {
            "image": img,
            "name": os.path.basename(img),
            "modes": {
                "visual": {"params": r_off["params"], "seconds": round(t_off, 1)},
                "hybrid": {"params": r_hyb["params"], "seconds": round(t_hyb, 1)},
                "ocr": {"params": ocr_pairs, "seconds": round(t_ocr, 1),
                        "raw_lines": [i["words"] for i in items]},
            },
            "quality": {
                "visual": quality(r_off["params"], known),
                "hybrid": quality(r_hyb["params"], known),
                "ocr": quality(ocr_pairs, known),
            },
            "consensus": consensus(r_off["params"], r_hyb["params"], ocr_pairs),
        }
        rows.append(row)
        q = row["quality"]
        c = row["consensus"]
        print(f"\n=== {row['name']}")
        for m in ("visual", "hybrid", "ocr"):
            x = q[m]
            print(f"  {m:7s} {x['n']:3d} 项  已知词表占比 {x['known_ratio']:.0%}  "
                  f"含数字/单位 {x['has_unit_ratio']:.0%}  可疑 {x['suspicious']}  "
                  f"({row['modes'][m]['seconds']}s)")
        print(f"  一致性: 共 {c['total_keys']} 键, 两两以上一致 {c['agree']}, "
              f"分歧 {c['disagree']}, 单一来源 {c['single_source']}")
        for k, vals in c["disagree_detail"][:4]:
            print(f"     分歧 {k}: {vals}")

    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


AREA_HINTS = {"内机", "外机", "型号", "颜色", "类别", "能效等级", "匹数",
              "额定制冷量", "额定制热量", "室内机噪音", "室外机噪音"}

if __name__ == "__main__":
    sys.exit(main())
