"""视觉参数提取：官方把参数放在图片里，接口不给。

实测结论（见 scripts/audit_usability.py）：
  整机 930 款中仅 83 款（8.9%）接口有结构化参数；
  其余 91% 的参数只存在于 PC 详情「规格参数」tab 的**长图**里。

本模块走 Flowlet 网关的视觉能力读取这些图，产出**带来源定位的断言** ——
定位形如 $.data.extend_info.desc_tabs_view[2].tab_content[0].plain_view.img#part1，
可回溯到具体哪张图的哪一段。

边界（必须遵守）：
  - 视觉抽取是**有损的**：数字可能读错，尤其小字/密集表格
  - 所有视觉断言标 source=mi_cn_pc_vision，与接口数据区分，不覆盖接口值
  - 必须记录 model 与抽取时间；冲突时接口数据优先
  - 长图按高度切片（<1800px/张），避免超限与漏读
"""
from __future__ import annotations
import base64
import json
import os
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .facts import Assertion, Capture, CaptureStatus

SRC_VISION = "mi_cn_pc_vision"
PARSER_VERSION = "vision-v1"

# Flowlet 网关（本机，带视觉）。密钥从环境或配置文件读取，不硬编码。
GATEWAY = os.environ.get("FLOWLET_GATEWAY", "http://127.0.0.1:18640")
MODEL = os.environ.get("FLOWLET_VISION_MODEL", "flowlet-flash")

SLICE_H = 1700          # 每片高度，实测 <1800 稳定
MAX_SLICES = 12         # 单图最多切 12 片，防失控


def _api_key() -> Optional[str]:
    """读取 Flowlet 网关密钥（不硬编码）。

    来源顺序：环境变量 -> Hermes profile .env 里的
    HERMES_CUSTOM_127_0_0_1_18640_API_KEY -> 个人 keys.env
    """
    for env in ("FLOWLET_API_KEY", "HERMES_CUSTOM_127_0_0_1_18640_API_KEY"):
        v = os.environ.get(env)
        if v:
            return v.strip()
    candidates = [
        "~/.hermes/profiles/myvault/.env",
        "~/.config/flowlet/key",
        "~/.config/herelens/keys.env",
    ]
    for p in candidates:
        fp = Path(os.path.expanduser(p))
        if not fp.exists():
            continue
        txt = fp.read_text(encoding="utf-8", errors="ignore")
        m = re.search(
            r"^\s*(?:export\s+)?(?:FLOWLET_API_KEY|HERMES_CUSTOM_127_0_0_1_18640_API_KEY"
            r"|FLOWLET_KEY|API_KEY)\s*=\s*[\"']?([^\s\"']+)",
            txt, re.M)
        if m and m.group(1) not in ("***", ""):
            return m.group(1)
    return None


def slice_image(path: str, outdir: str, slice_h: int = SLICE_H) -> list[dict]:
    """长图切片，返回 [{path, index, y0, y1}]"""
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    im = Image.open(path)
    W, H = im.size
    parts = []
    n = min((H + slice_h - 1) // slice_h, MAX_SLICES)
    for i in range(n):
        y0, y1 = i * slice_h, min((i + 1) * slice_h, H)
        fp = os.path.join(outdir, f"{Path(path).stem}_p{i}.png")
        im.crop((0, y0, W, y1)).save(fp)
        parts.append({"path": fp, "index": i, "y0": y0, "y1": y1})
    return parts


PROMPT = """这是小米商品官方「规格参数」长图的第 {i} 段（共 {n} 段）。
请提取图中所有参数名与对应值，输出**严格 JSON**：{{"params": {{"参数名": "值", ...}}}}
要求：
- 只提取真实可见的文字，不推测、不补全
- 值里的单位原样保留（如 "3500W"、"5.27"、"37-41dB(A)"）
- 看不清的项不要输出，不要写"不清晰"
- 表格按"参数名: 值"展开
- 只输出 JSON，不要任何解释"""


def extract_params_from_image(img_path: str, gateway: str = GATEWAY,
                              api_key: Optional[str] = None,
                              outdir: Optional[str] = None) -> dict:
    """对一张（长）图做视觉参数提取。返回 {params, parts, errors}"""
    key = api_key or _api_key()
    if not key:
        return {"ok": False, "reason": "no_api_key",
                "params": {}, "parts": [], "errors": ["缺少 Flowlet 密钥"]}
    outdir = outdir or "/tmp/goodsdex-vision"
    parts = slice_image(img_path, outdir)
    params, errors = {}, []
    for p in parts:
        try:
            got = _ask_vision(p["path"], p["index"], len(parts), gateway, key)
            for k, v in (got or {}).items():
                k = str(k).strip()
                if k and k not in params:
                    params[k] = str(v).strip()
        except Exception as e:
            errors.append(f"part{p['index']}: {type(e).__name__}: {e}")
    # 归一化：收敛同义写法、分离包装附件（否则无法跨商品对比）
    from .vision_normalize import canonicalize_params
    canon, aliases, accessories = canonicalize_params(params)
    return {"ok": bool(canon), "params": canon, "raw_params": params,
            "aliases": aliases, "accessories": accessories,
            "parts": parts, "errors": errors}


def _ask_vision(img_path: str, idx: int, total: int, gateway: str, key: str) -> dict:
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    body = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT.format(i=idx + 1, n=total)},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ],
        }],
    }
    req = urllib.request.Request(
        gateway.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read().decode())
    text = (resp.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}
    try:
        return (json.loads(m.group(0)) or {}).get("params") or {}
    except Exception:
        return {}


def to_assertions(img_url: str, tab_index: int, part_index: int, params: dict,
                  subject_id: str, aliases: dict | None = None) -> tuple[list[Capture], list[Assertion]]:
    """把视觉结果转成断言（来源可定位到具体图片片段）。

    属性名已归一化；aliases 记录 raw -> canonical 的映射，供复核。
    """
    cap = Capture.make(SRC_VISION, img_url, json.dumps(params, ensure_ascii=False),
                       parser_version=PARSER_VERSION)
    out = []
    for k, v in params.items():
        out.append(Assertion(
            assertion_id=f"{cap.capture_id}:{k}",
            subject_id=subject_id, capture_id=cap.capture_id, source=SRC_VISION,
            attribute=k, raw_value=v,
            locator=f"$.data.extend_info.desc_tabs_view[{tab_index}]"
                    f".tab_content[{part_index}].plain_view.img",
            ui_location=("规格参数" + (
                f"（归一化自 {len(aliases[k])} 种写法）"
                if aliases and len(aliases.get(k, [])) > 1 else "")),
            page="PC 商品详情页（图片）",
            parser_version=PARSER_VERSION))
    return [cap], out


if __name__ == "__main__":
    import sys
    key = _api_key()
    print("Flowlet 密钥:", "已配置" if key else "未配置")
    print("网关:", GATEWAY, "| 模型:", MODEL)
    if len(sys.argv) > 1:
        r = extract_params_from_image(sys.argv[1])
        print(json.dumps(r["params"], ensure_ascii=False, indent=1)[:1500])
        if r["errors"]:
            print("错误:", r["errors"])
