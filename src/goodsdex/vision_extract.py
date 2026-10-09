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

# 混合模式：把 OCR 文本一并给模型，让它专注做结构理解
PROMPT_HYBRID = """这是小米商品官方「规格参数」长图的第 {i} 段（共 {n} 段）。

下面是用 OCR 从**同一张图**识别出的原始文本行（按从上到下、从左到右顺序）。
OCR 的**文字识别是准确的**，但它不知道哪些是参数名、哪些是值，
也不懂表格结构 —— 请你结合**图片**和**这些文本**，完成结构理解。

【OCR 文本行】
{ocr_text}

请输出**严格 JSON**：{{"params": {{"参数名": "值", ...}}}}
要求：
- 以图片为准，OCR 文本作为辅助（可用于确认易混字、数字）
- 只提取真实存在的参数，不推测、不补全
- 值里的单位原样保留（如 "3500W"、"5.27"、"37-41dB(A)"）
- OCR 文本若把一行拆成多行（如 "860" 与 "(75-1950)"），请合并成完整值
- 只输出 JSON，不要任何解释"""


def _baidu_ocr_lines(img_path: str) -> str:
    """用百度 OCR 取图片文本行（失败返回空串，不阻断流程）"""
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
        from ocr_compare import baidu_token, load_keys, ocr_general
        k = load_keys()
        if not k.get("BAIDU_OCR_API_KEY"):
            return ""
        res = ocr_general(img_path, baidu_token(k))
        return "\n".join(w.get("words", "") for w in res.get("words_result", []))
    except Exception:
        return ""


def extract_params_from_image(img_path: str, gateway: str = GATEWAY,
                              api_key: Optional[str] = None,
                              outdir: Optional[str] = None,
                              ocr: str = "off") -> dict:
    """对一张（长）图做视觉参数提取。

    ocr 模式：
      off    只给图片（原行为）
      hybrid 图片 + OCR 文本一起给模型 —— 让模型专注结构理解，
             绕开"自己写配对启发式"的脆弱环节（实测手写配对最好只有 67%）
      only   只用 OCR，不调模型（最省，但需自己配对）
    """
    key = api_key or _api_key()
    if not key and ocr != "only":
        return {"ok": False, "reason": "no_api_key",
                "params": {}, "parts": [], "errors": ["缺少 Flowlet 密钥"]}
    outdir = outdir or "/tmp/goodsdex-vision"
    parts = slice_image(img_path, outdir)
    params, errors = {}, []
    observations: dict[str, list] = {}     # 同名参数的多片观测值

    if ocr == "only":
        txt = _baidu_ocr_lines(img_path)
        return {"ok": bool(txt), "params": {}, "raw_ocr": txt,
                "parts": parts, "errors": [] if txt else ["OCR 无输出"]}

    model_outputs: dict[int, str] = {}
    for p in parts:
        try:
            ocr_text = ""
            if ocr == "hybrid":
                ocr_text = _baidu_ocr_lines(p["path"])
            got, mtext = _ask_vision(p["path"], p["index"], len(parts), gateway, key,
                                     ocr_text=ocr_text)
            model_outputs[p["index"]] = mtext
            for k, v in (got or {}).items():
                k = str(k).strip()
                if not k:
                    continue
                v = str(v).strip()
                # 不静默丢弃：同一参数名在多个切片出现时，两值都要保留
                # （与 facts.py 的原则一致 —— 多源/多次观测是独立佐证）
                prev = params.get(k)
                if prev is None:
                    params[k] = v
                elif prev != v:
                    existing = observations.setdefault(k, [prev])
                    if v not in existing:
                        existing.append(v)
        except Exception as e:
            errors.append(f"part{p['index']}: {type(e).__name__}: {e}")
    # 归一化：收敛同义写法、分离包装附件（否则无法跨商品对比）
    from .vision_normalize import canonicalize_params
    canon, aliases, accessories = canonicalize_params(params)
    return {"ok": bool(canon), "params": canon, "raw_params": params,
            "aliases": aliases, "accessories": accessories,
            "observations": observations,
            "parts": parts, "errors": errors, "ocr_mode": ocr,
            "model_outputs": model_outputs}


def _ask_vision(img_path: str, idx: int, total: int, gateway: str, key: str,
                ocr_text: str = "") -> dict:
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    if ocr_text:
        prompt = PROMPT_HYBRID.format(i=idx + 1, n=total, ocr_text=ocr_text)
    else:
        prompt = PROMPT.format(i=idx + 1, n=total)
    body = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
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
        return {}, text
    try:
        return ((json.loads(m.group(0)) or {}).get("params") or {}), text
    except Exception:
        return {}, text


def to_assertions(img_url: str, tab_index: int, part_index: int, params: dict,
                  subject_id: str, aliases: dict | None = None,
                  image_sha256: str = "", model_text: str = "",
                  parent_capture_id: str = "",
                  part_range: tuple[int, int] | None = None,
                  ) -> tuple[list[Capture], list[Assertion]]:
    """把视觉结果转成断言。

    **证据必须是证据，不能是答案**（Codex 评审指认）：
      原实现把 json.dumps(params) 当作 response_raw，而 locator 写成
      `...desc_tabs_view[N].tab_content[M].plain_view.img` —— 这个路径
      在那份 JSON 里**不可能解析**，等于写了个看着能定位、实际指向空处的路径。

    改为：capture 里保存**可核验的派生证据**，字段名不再冒充原始响应：
      - source_image_url / source_image_sha256：实际处理的那张图
      - model_raw_output：模型原始输出文本
      - model / prompt_version / parser_version：可复现所需配置
      - parent_capture_id：父 PC 响应（图从哪来）
      - slice_range：长图切片范围 [y0, y1]
    locator 改为指向 **capture 自身结构 + 切片**，可真实解析。
    """
    import hashlib
    evidence = {
        "type": "vision_extraction",
        "source_image_url": img_url,
        "source_image_sha256": image_sha256,
        "tab_index": tab_index,
        "part_index": part_index,
        "slice_range": list(part_range) if part_range else None,
        "model": MODEL,
        "prompt_version": PARSER_VERSION,
        "parent_capture_id": parent_capture_id,
        "model_raw_output": model_text,
        "extracted": params,
    }
    cap = Capture.make(SRC_VISION, img_url,
                       json.dumps(evidence, ensure_ascii=False),
                       parser_version=PARSER_VERSION)
    out = []
    for k, v in params.items():
        out.append(Assertion(
            assertion_id=f"{cap.capture_id}:{k}",
            subject_id=subject_id, capture_id=cap.capture_id, source=SRC_VISION,
            attribute=k, raw_value=v,
            # 指向 capture 内的真实结构（可解析），而非不存在的原始响应路径
            locator=f"$.extracted.{k}",
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
