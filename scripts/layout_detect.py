"""排版判定：这张图是「规整表格」还是「标识/图文」？

由来（实测）：
  空调 spec_0（规整两列表）  -> OCR 0.6s，结果正确
  空调 spec_1（能效标识+清单）-> OCR 结果错乱（"1级"->"11级"、"王"->"能效标识…"）
  同一张 spec_1，视觉 LLM 结果干净。
  所以关键不是"OCR vs 视觉"，而是**先判断排版**，再分流。

两个互补信号：

  ① 布局特征（事前）
     - x 坐标双峰性：规整表格的文本块左边界会聚成 2 个峰（名名列、值列）
     - 行高一致性：表格字号统一（高度变异系数低）
     - 行数/块数比：表格块多且分布规则

  ② 配对自检（事后）
     - 污染率：若提取出的「值」里包含「键」本身的文字，
       说明配对错位（实测 spec_1 出现 "3500额定制冷量(W)3500"）
     - 这是**不依赖外部标准答案**的自检，可直接用于流水线
"""
from __future__ import annotations
import re
from collections import Counter


def layout_features(items: list[dict]) -> dict:
    """从含坐标的 OCR 块计算布局特征"""
    if not items:
        return {"n": 0}
    lefts = [it["left"] for it in items]
    heights = [it["height"] for it in items if it.get("height")]
    if not heights:
        return {"n": len(items)}

    med_h = sorted(heights)[len(heights) // 2] or 20
    # 高度一致性（变异系数，越低越像表格）
    mean_h = sum(heights) / len(heights)
    var = sum((h - mean_h) ** 2 for h in heights) / len(heights)
    cv_h = (var ** 0.5) / mean_h if mean_h else 9.9

    # x 坐标分桶（桶宽 = 中位字高的 1.5 倍）
    bw = max(int(med_h * 1.5), 10)
    bins = Counter(int(l // bw) for l in lefts)
    # 峰数：计数 >= 总数的 15% 的桶
    thresh = max(len(lefts) * 0.15, 3)
    peaks = sorted([b for b, c in bins.items() if c >= thresh])
    # 双峰性：最强两个峰的间距是否显著
    top2 = [b for b, _ in bins.most_common(2)]
    peak_gap = (max(top2) - min(top2)) * bw if len(top2) == 2 else 0

    # 行数（按 top 聚类）
    tol = med_h * 0.6
    rows = []
    for it in sorted(items, key=lambda x: x["top"]):
        if rows and abs(rows[-1][0] - it["top"]) <= tol:
            rows[-1][1] += 1
        else:
            rows.append([it["top"], 1])
    multi = sum(1 for _, c in rows if c >= 2)      # 一行有多个块

    return {
        "n": len(items),
        "med_h": med_h,
        "height_cv": round(cv_h, 3),
        "peak_count": len(peaks),
        "peak_gap_px": peak_gap,
        "rows": len(rows),
        "multi_block_rows": multi,
        "multi_row_ratio": round(multi / max(len(rows), 1), 3),
        "blocks_per_row": round(len(items) / max(len(rows), 1), 2),
    }


def classify_layout(f: dict) -> str:
    """判定排版类型：table | label | unknown

    table  -> 适合 OCR（规整双列，行内多块，字号统一）
    label  -> 适合视觉（标识/图文混排，行内块少或字号差异大）
    """
    if not f or f.get("n", 0) < 6:
        return "unknown"
    # 表格特征：多数行含 ≥2 块（名副其实的行内左右两列）+ 字号统一
    if f["multi_row_ratio"] >= 0.45 and f["height_cv"] <= 0.55:
        return "table"
    # 标识类：几乎每行只有一个块（文字顺着往下排，不是左右两列）
    if f["multi_row_ratio"] <= 0.25:
        return "label"
    return "unknown"


def contamination(pairs: dict) -> dict:
    """配对自检：值里含键的文字 = 配对错位（不需要外部标准答案）"""
    if not pairs:
        return {"n": 0, "bad": 0, "rate": 0.0, "samples": []}
    bad = []
    for k, v in pairs.items():
        ks = re.sub(r"\s", "", str(k))
        vs = re.sub(r"\s", "", str(v))
        if len(ks) >= 3 and ks in vs:
            bad.append((k, str(v)[:40]))
    return {"n": len(pairs), "bad": len(bad),
            "rate": round(len(bad) / len(pairs), 3),
            "samples": bad[:5]}


def route(f: dict, pairs: dict | None = None,
          contamination_rate: float = 0.0) -> tuple[str, str]:
    """决定用哪条路。返回 (route, reason)

    实测教训：**几何特征不足以判断**。
    spec_1（能效标识图）几何上像表格（行内多块 0.82、字号统一），
    但文字语义错位（标签与值不在同一行），OCR 结果完全不可用。
    靠污染率才识别出来。

    所以判据以**污染率 + 有效配对量**为主，几何为辅：
      1. 配对量太少（< 5）-> OCR 没读到实质内容，不可信
      2. 污染率高（>= 15%）-> 值里含键的文字，配对错位
      3. 两者都过关 -> OCR 可用（快、免费）
    """
    n = len(pairs or {})
    if n < 5:
        return "vision", f"OCR 有效配对仅 {n} 对，覆盖不足"
    if contamination_rate >= 0.15:
        return "vision", f"OCR 配对污染率 {contamination_rate:.0%}，键值错位"
    layout = classify_layout(f)
    if contamination_rate < 0.05 and n >= 8:
        return "ocr", (f"配对自洽（污染 {contamination_rate:.0%}，{n} 对），"
                       f"布局似表格，OCR 划算")
    return "vision", (f"污染率 {contamination_rate:.0%} 偏高但未超标，"
                      f"保守走视觉")


if __name__ == "__main__":
    import json
    import os
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from ocr_compare import load_keys, baidu_token
    from ocr_position import ocr_with_location, pair_by_position

    token = baidu_token(load_keys())
    print(f"{'图':16s}{'块':>4s}{'行':>4s}{'行内多块':>8s}{'字号CV':>8s}"
          f"{'峰':>3s}{'污染率':>7s}  判定")
    for img in sys.argv[1:]:
        items = ocr_with_location(img, token)
        f = layout_features(items)
        pairs = pair_by_position(items)
        c = contamination(pairs)
        rt, why = route(f, pairs, c["rate"])
        print(f"{os.path.basename(img):16s}{f.get('n',0):>4d}{f.get('rows',0):>4d}"
              f"{f.get('multi_row_ratio',0):>8.2f}{f.get('height_cv',0):>8.2f}"
              f"{f.get('peak_count',0):>3d}{c['rate']:>7.0%}  "
              f"{rt:7s} {why}")
        if c["samples"]:
            print(f"      污染样例: {c['samples'][:2]}")
