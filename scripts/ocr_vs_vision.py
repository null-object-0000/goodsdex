"""对照实验：百度 OCR vs 视觉 LLM（同一张规格图）

衡量方式：以人工核对过的基准为参照，算字段级准确率。
不看"能不能读出来"，看**参数名与值的配对是否正确**。
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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from ocr_compare import baidu_token, load_keys, ocr_general

# 人工核对的基准（从图里逐项确认过）
GROUND_TRUTH = {
    "型号": "KFR-35GW/N1A1",
    "颜色": "白色",
    "类别": "分体挂壁式（挂机）",
    "制冷类型": "冷暖",
    "匹数": "1.5匹",
    "定/变频": "变频",
    "能效等级": "新1级",
    "APF": "5.27",
    "额定制冷量(W)": "3500(150-5100)",
    "额定制冷功率(W)": "860(75-1950)",
    "额定制热量(W)": "5000(150-6610)",
    "额定制热功率(W)": "1300(90-2050)",
    "内机宽度": "840mm",
    "内机高度": "311mm",
    "内机深度": "200mm",
    "外机宽度": "860mm",
    "外机高度": "551mm",
    "外机深度": "331mm",
}


def norm(s: str) -> str:
    """归一化用于对比：全角半角、空格、括号"""
    import unicodedata
    s = unicodedata.normalize("NFKC", str(s or ""))
    for a, b in {"（": "(", "）": ")", " ": "", "　": "", "*": "",
                 "：": ":", "，": ","}.items():
        s = s.replace(a, b)
    return s.strip().lower()


def ocr_pairs(words: list[str]) -> dict:
    """把 OCR 文本行配对成 {参数名: 值}。

    实测发现（百度 OCR 对规格表的输出）：
      - 认字准确率 100%
      - **行顺序是"参数名、值、参数名、值"完美交替**
        （型号 / KFR-35GW/N1A1 / 颜色 / 白色 / 类别 / 分体挂壁式(挂机) …）
      - 唯一例外：长值会被换行拆开（"860" + "(75-1950)"）

    所以配对规则很简单：名字行与值行交替；若值以未闭合括号结尾，
    则与下一行拼接。
    """
    NAME_RE = re.compile(r"^[\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z()（）/\-*·\s]{0,30}$")

    def is_name(s: str) -> bool:
        """名字行：纯中文/英文词，通常**不含数字**（型号里的数字除外，但
        "KFR-35GW"这种以字母开头且含数字的更像值）。

        实测判据：名字行的常见形态是"额定制冷量(W)"这类 —— 中文开头，
        可能带单位括号；而值行往往以数字开头，或含 mm/L/W 等单位。
        """
        if not s or len(s) > 30:
            return False
        if not NAME_RE.match(s):
            return False
        # 含单位数字的更像值
        if re.match(r"^[\d\-+]", s):
            return False
        if re.search(r"\d+\s*(mm|cm|m|L|kg|g|W|dB|Hz|V|匹|级|GB|TB|Pa|rpm)\b", s, re.I):
            return False
        return True

    pairs, pending = {}, None
    for raw in words:
        s = raw.strip()
        if not s:
            continue
        if is_name(s) and pending is None:
            pending = s
            pairs.setdefault(s, "")
            continue
        if pending is not None:
            cur = pairs.get(pending, "")
            pairs[pending] = (cur + s) if cur else s
            # 值闭合（不以未闭括号结尾）则结束该字段
            if not re.search(r"[(\[]\s*\d*\s*$", pairs[pending]):
                pending = None
        # 孤立的值行（没有待配名）忽略
    return pairs


def main() -> int:
    img = sys.argv[1] if len(sys.argv) > 1 else "/tmp/gd/spec_0.jpg"
    print("=" * 74)
    print("对照实验：百度 OCR vs 视觉 LLM")
    print("=" * 74)

    # ---- OCR ----
    k = load_keys()
    tk = baidu_token(k)
    res = ocr_general(img, tk)
    words = [w.get("words", "") for w in res.get("words_result", [])]
    o_pairs = ocr_pairs(words)

    # ---- 视觉 LLM ----
    from goodsdex.vision_extract import extract_params_from_image
    vr = extract_params_from_image(img)
    v_pairs = vr["params"]

    print(f"\nOCR 原始行数   {len(words)}")
    print(f"OCR 配对成功   {len(o_pairs)} 对")
    print(f"视觉 LLM 提取  {len(v_pairs)} 项")

    def score(pairs: dict, label: str):
        hit = 0
        detail = []
        for gk, gv in GROUND_TRUTH.items():
            # 在候选里找键名相近的
            matched = None
            for pk in pairs:
                if norm(gk) in norm(pk) or norm(pk) in norm(gk):
                    matched = pk
                    break
            if matched is None:
                detail.append(("缺失", gk, gv, ""))
                continue
            ok = norm(gv).replace("(", "").replace(")", "") in \
                 norm(pairs[matched]).replace("(", "").replace(")", "")
            if ok:
                hit += 1
            else:
                detail.append(("值不符", gk, gv, pairs[matched]))
        print(f"\n{label}: {hit}/{len(GROUND_TRUTH)} = {hit/len(GROUND_TRUTH):.0%}")
        for kind, gk, gv, got in detail[:8]:
            print(f"    {kind}: {gk} 期望={gv} 实得={got or '—'}")
        return hit

    h1 = score(o_pairs, "OCR（通用文字识别 + 行配对）")
    h2 = score(v_pairs, "视觉 LLM（结构化 JSON）")

    print("\n" + "=" * 74)
    print(f"结论：OCR {h1}/{len(GROUND_TRUTH)}  vs  视觉 {h2}/{len(GROUND_TRUTH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
