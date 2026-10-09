"""公平对照实验：OCR vs 视觉 LLM，用**接口参数**当基准。

为什么重新做（上一版的缺陷）：
  1. 只测了 1 张图 —— 样本量为 1，不足以下结论
  2. ground truth 是我手敲的 18 项 —— 测的是"我的细心程度"
  3. OCR 配对逻辑是我写的 —— 测出的是"我的代码水平"，
     而不是"OCR 本身的能力"

本版设计：
  - 基准 = **接口参数**（官方结构化数据，独立于我）
  - 同一张规格图，两种方法各自提取
  - 逐字段判定：提取到了吗？值对吗？
  - 跨多个品类、多张图

评估指标：
  召回 recall   = 接口有的参数里，方法成功恢复的比例
  精度 precision = 方法给出的值里，与接口一致的比例
  （图片里可能有接口没有的参数 —— 那算增量，不计为错误）
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

from vision_params import find_spec_images
from vision_params_lib import META_FIELDS, count_real_params


def norm_key(k: str) -> str:
    """键名归一化：全角->半角、去空格/括号/单位后缀"""
    import unicodedata
    s = unicodedata.normalize("NFKC", str(k or ""))
    for a, b in {"（": "(", "）": ")", " ": "", "　": "", "*": "", "-": "",
                 "：": "", "、": "", "/": ""}.items():
        s = s.replace(a, b)
    s = re.sub(r"\((w|w)\)", "", s, flags=re.I)
    return s.strip().lower()


def norm_val(v) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKC", str(v or ""))
    for a, b in {"（": "(", "）": ")", " ": "", "　": ""}.items():
        s = s.replace(a, b)
    return s.strip().lower()


def similar(a: str, b: str) -> bool:
    """值是否等价（允许一方包含另一方，如 '860' vs '860(75-1950)'）"""
    na, nb = norm_val(a), norm_val(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    # 数字全等
    da = re.findall(r"\d+(?:\.\d+)?", na)
    db = re.findall(r"\d+(?:\.\d+)?", nb)
    if da and da == db:
        return True
    return na in nb or nb in na


def key_match(bk: str, cand: dict) -> str | None:
    """在候选键里找与基准键对应的（归一化后互相包含）"""
    nb = norm_key(bk)
    for ck in cand:
        nc = norm_key(ck)
        if nb == nc or (len(nb) >= 3 and nb in nc) or (len(nc) >= 3 and nc in nb):
            return ck
    return None


def evaluate(baseline: dict, got: dict, label: str) -> dict:
    """以 baseline（接口参数）为准，评估 got 的召回与精度"""
    hit, miss = [], []
    for bk, bv in baseline.items():
        ck = key_match(bk, got)
        if ck is None:
            miss.append((bk, bv, "未提取"))
            continue
        if similar(bv, got[ck]):
            hit.append(bk)
        else:
            miss.append((bk, bv, f"值不符: {got[ck]}"))
    # 精度：给出的值里，有多少能在基准里找到对应且一致
    tp = 0
    extra = []
    for ck, cv in got.items():
        bk = key_match(ck, baseline)
        if bk is None:
            extra.append(ck)          # 接口没有 -> 增量，不算错
        elif similar(cv, baseline[bk]):
            tp += 1
    recall = len(hit) / max(len(baseline), 1)
    precision = tp / max(len(got), 1)
    return {"label": label, "recall": recall, "precision": precision,
            "baseline_n": len(baseline), "got_n": len(got),
            "hits": hit, "misses": miss, "extras": extra}
