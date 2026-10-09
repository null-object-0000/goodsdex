"""OCR 位置版对比：用坐标配对，而不是靠猜。

实测教训（这个文件是第三次尝试）：
  第 1 版：靠"值以字母/括号结尾"截断 -> 9/18
  第 2 版：靠"名字行不含数字"判断      -> 8/18（KFR-35GW/N1A1 被当成名字）

  手写启发式连错两次，说明**靠文本猜结构不靠谱**。
  正解：让 OCR 返回**坐标**，同行的左右两列就是 名字/值 —— 确定性配对。

百度 OCR 高精度含位置版：/rest/2.0/ocr/v1/accurate
  参数 vertexes_location=true -> words_result[].location {left, top, width, height}
"""
from __future__ import annotations
import base64
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from ocr_compare import load_keys, baidu_token


def ocr_with_location(img: str, token: str) -> list[dict]:
    """高精度含位置版 OCR，返回 [{words, left, top, width, height}]"""
    with open(img, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    body = urllib.parse.urlencode({
        "image": b64, "vertexes_location": "true"}).encode()
    req = urllib.request.Request(
        "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=" + token,
        data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=90) as r:
        res = json.loads(r.read().decode())
    out = []
    for w in res.get("words_result", []):
        loc = w.get("location") or {}
        out.append({"words": w.get("words", ""),
                    "left": loc.get("left", 0), "top": loc.get("top", 0),
                    "width": loc.get("width", 0), "height": loc.get("height", 0)})
    return out


def pair_by_position(items: list[dict], y_tol_ratio: float = 0.6) -> dict:
    """按坐标配对：同一水平带内的左列 = 名，右列 = 值。

    y_tol_ratio: 判定"同一行"的纵向容差（相对行高的比例）
    """
    if not items:
        return {}
    h = sorted(x["height"] for x in items)[len(items) // 2] or 20
    tol = h * y_tol_ratio

    # 按 top 聚成行
    rows: list[list[dict]] = []
    for it in sorted(items, key=lambda x: (x["top"], x["left"])):
        placed = False
        for row in rows:
            if abs(row[0]["top"] - it["top"]) <= tol:
                row.append(it)
                placed = True
                break
        if not placed:
            rows.append([it])

    pairs = {}
    for row in rows:
        row = sorted(row, key=lambda x: x["left"])
        if len(row) < 2:
            continue
        name = row[0]["words"].strip()
        val = "".join(x["words"] for x in row[1:]).strip()
        if not name or not val:
            continue
        # 名字不该是纯值（含大量数字且无中文）
        if re.fullmatch(r"[\d\s().\-+/|]*", name):
            continue
        if name in pairs and len(pairs[name]) >= len(val):
            continue
        pairs[name] = val
    return pairs


GROUND_TRUTH = {
    "型号": "KFR-35GW/N1A1", "颜色": "白色", "类别": "分体挂壁式（挂机）",
    "制冷类型": "冷暖", "匹数": "1.5匹", "定/变频": "变频", "能效等级": "新1级",
    "APF": "5.27", "额定制冷量(W)": "3500(150-5100)",
    "额定制冷功率(W)": "860(75-1950)", "额定制热量(W)": "5000(150-6610)",
    "额定制热功率(W)": "1300(90-2050)", "内机宽度": "840mm",
    "内机高度": "311mm", "内机深度": "200mm", "外机宽度": "860mm",
    "外机高度": "551mm", "外机深度": "331mm",
}


def norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKC", str(s or ""))
    for a, b in {"（": "(", "）": ")", " ": "", "*": "", "：": ":"}.items():
        s = s.replace(a, b)
    return s.strip().lower()


def score(pairs: dict, label: str) -> int:
    hit, detail = 0, []
    for gk, gv in GROUND_TRUTH.items():
        matched = next((pk for pk in pairs
                        if norm(gk) in norm(pk) or norm(pk) in norm(gk)), None)
        if matched is None:
            detail.append(("缺失", gk, gv, ""))
            continue
        if norm(gv).replace("(", "").replace(")", "") in \
           norm(pairs[matched]).replace("(", "").replace(")", ""):
            hit += 1
        else:
            detail.append(("值不符", gk, gv, pairs[matched]))
    print(f"\n{label}: {hit}/{len(GROUND_TRUTH)} = {hit/len(GROUND_TRUTH):.0%}")
    for kind, gk, gv, got in detail[:6]:
        print(f"    {kind}: {gk} 期望={gv} 实得={got or '—'}")
    return hit


if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else "/tmp/gd/spec_0.jpg"
    k = load_keys()
    tk = baidu_token(k)
    items = ocr_with_location(img, tk)
    print(f"含位置 OCR 返回 {len(items)} 个文本块")
    print("\n前 12 块（坐标）：")
    for it in sorted(items, key=lambda x: (x["top"], x["left"]))[:12]:
        print(f"  top={it['top']:5d} left={it['left']:5d} "
              f"{it['width']:4d}x{it['height']:3d}  {it['words']}")

    p = pair_by_position(items)
    print(f"\n按坐标配对 {len(p)} 对：")
    for kk, vv in list(p.items())[:16]:
        print(f"    {kk[:28]:30s} = {vv[:30]}")

    h_ocr = score(p, "OCR（坐标配对）")

    from goodsdex.vision_extract import extract_params_from_image
    vr = extract_params_from_image(img)
    h_vis = score(vr["params"], "视觉 LLM")

    print(f"\n{'='*70}\n结论：OCR+坐标 {h_ocr}/{len(GROUND_TRUTH)}"
          f"  vs  视觉 {h_vis}/{len(GROUND_TRUTH)}")
