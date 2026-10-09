"""对照实验：百度 OCR vs 视觉 LLM 提取同一张规格图。

用途：回答"能不能用 OCR 替代视觉 LLM"。
不看主观印象，用**字段级准确率**对比。

百度 OCR 走通用文字识别（高精度版）+ 表格识别。
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

KEYS = Path(os.path.expanduser("~/.config/herelens/keys.env"))


def load_keys() -> dict:
    out = {}
    if not KEYS.exists():
        return out
    for line in KEYS.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip().replace("export ", "").strip()] = v.strip().strip('"').strip("'")
    return out


def baidu_token(k: dict) -> str:
    url = ("https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials"
           f"&client_id={k['BAIDU_OCR_API_KEY']}&client_secret={k['BAIDU_OCR_SECRET_KEY']}")
    with urllib.request.urlopen(url, timeout=25) as r:
        return json.loads(r.read().decode())["access_token"]


def ocr_general(img: str, token: str, accurate: bool = True) -> dict:
    """通用文字识别"""
    ep = ("https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic" if accurate
          else "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic")
    with open(img, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    body = urllib.parse.urlencode({"image": img_b64}).encode()
    req = urllib.request.Request(
        f"{ep}?access_token={token}", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def ocr_table(img: str, token: str) -> dict:
    """表格文字识别（异步接口，含提交+轮询）"""
    import time
    with open(img, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    body = urllib.parse.urlencode({"image": img_b64}).encode()
    req = urllib.request.Request(
        f"https://aip.baidubce.com/rest/2.0/ocr/v1/table?access_token={token}",
        data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read().decode())
    rid = res.get("result", {}).get("request_id")
    if not rid:
        return res
    for _ in range(30):
        time.sleep(2)
        q = urllib.request.Request(
            f"https://aip.baidubce.com/rest/2.0/ocr/v1/table/result"
            f"?access_token={token}&request_id={rid}")
        with urllib.request.urlopen(q, timeout=30) as r:
            r2 = json.loads(r.read().decode())
        if r2.get("result", {}).get("ret_code") == 1:
            return r2
    return {"error": "table timeout"}


def words_to_pairs(words: list[str]) -> dict:
    """把 OCR 文本行粗暴配成 参数名=值。

    规格表是"名 值"左右两列，OCR 通常按行返回或按块返回。
    这里做启发式配对：以行合并后，按"是否含单位/数字"判断值。
    """
    pairs = {}
    for i, w in enumerate(words):
        s = w.strip()
        if not s:
            continue
        # 形如 "型号 KFR-35GW/N1A1"
        m = re.match(r"^([\u4e00-\u9fffA-Za-z()（）%/\-\s]{2,20}?)[\s:：]+(.+)$", s)
        if m:
            pairs[m.group(1).strip()] = m.group(2).strip()
    return pairs


if __name__ == "__main__":
    img = sys.argv[1]
    k = load_keys()
    if not k.get("BAIDU_OCR_API_KEY"):
        print("缺少百度 OCR 凭据")
        sys.exit(1)
    print("获取 token...")
    tk = baidu_token(k)
    print("token ok, len:", len(tk))
    res = ocr_general(img, tk)
    words = [w.get("words", "") for w in res.get("words_result", [])]
    print(f"\n通用OCR 识别 {len(words)} 行")
    for w in words[:40]:
        print("  ", w)
    print(f"\nwords_result_num={res.get('words_result_num')}")
