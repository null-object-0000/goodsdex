"""转转开放平台残值源。

官方文档（免登录可读）：https://developer.zhuanzhuan.com/docs
  回收估价   POST /zaimcp/recycle_valuation   图片/描述 -> 回收价区间
  成交行情   POST /zaimcp/market_price        型号 -> 最新一期成交价区间

**重要**：调用需要开放平台账号（手机号注册 + 短信验证）。
本模块不存账号密码 —— 凭证放仓库外 ~/.config/goodsdex/zhuanzhuan.env，
由使用者自行注册后填写（扫码/验证码登录由人工完成）。

为什么这条源关键：
  小米官方保值换新的回收方就是**转转循环科技**，所以转转的估价
  与官方以旧换新的实际回收额同源，可信度高于任何第三方估算。
"""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from ..economics import ResidualQuote

CRED_PATH = Path(os.path.expanduser("~/.config/goodsdex/zhuanzhuan.env"))
BASE = "https://developer.zhuanzhuan.com/zaimcp"

# 端点契约（来自官方公开文档，字段名已确认）
ENDPOINTS = {
    "recycle_valuation": {
        "path": "/recycle_valuation",
        "params": ["query", "images"],
        "returns": {"price.min_value": "最低价", "price.max_value": "最高价",
                    "price.granularity": "detail|model_reference|series_reference",
                    "product.display_name": "识别出的商品名",
                    "product.confidence": "识别置信度 0-1",
                    "status": "valued|need_input|handoff|degraded|conflict|failed"},
    },
    "market_price": {
        "path": "/market_price",
        "params": ["keyword", "userIntent", "filterCriteria"],
        "returns": {"data.dealMinPrice": "最新一期成交最低价",
                    "data.dealMaxPrice": "最新一期成交最高价",
                    "data.jumpUrl": "行情查看链接"},
    },
}


def load_credentials() -> Optional[dict]:
    """读取凭证（仓库外）。不存在则返回 None，调用方须明确说明缺凭证。"""
    if not CRED_PATH.exists():
        return None
    creds = {}
    for line in CRED_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip().strip('"').strip("'")
    return creds or None


def credentials_status() -> dict:
    """凭证状态（不回显任何密钥内容）"""
    c = load_credentials()
    if not c:
        return {"configured": False,
                "path": str(CRED_PATH),
                "action": "请在转转开放平台注册账号后，把凭证写入该文件（见模块顶部说明）"}
    keys = sorted(k for k in c if k)
    return {"configured": True, "path": str(CRED_PATH), "keys": keys}


def _post(path: str, payload: dict, creds: dict, timeout: int = 25) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 # 凭证字段名以开放平台控制台实际发放为准
                 **{k: v for k, v in creds.items()
                    if k.lower() in ("appkey", "appsecret", "token", "authorization")}},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def query_market_price(keyword: str, filter_criteria: str = "",
                       creds: Optional[dict] = None) -> dict:
    """查询二手成交价区间。返回结构化结果（含失败原因，不伪装成功）"""
    creds = creds or load_credentials()
    if not creds:
        return {"ok": False, "reason": "no_credentials",
                "action": credentials_status()["action"]}
    try:
        resp = _post("/market_price",
                     {"keyword": keyword, "userIntent": "", "filterCriteria": filter_criteria},
                     creds)
    except urllib.error.HTTPError as e:
        return {"ok": False, "reason": f"http_{e.code}", "detail": e.read()[:300].decode("utf-8", "ignore")}
    except Exception as e:
        return {"ok": False, "reason": f"{type(e).__name__}", "detail": str(e)}

    if resp.get("code") != 0:
        return {"ok": False, "reason": "business_error", "detail": resp.get("message")}
    d = resp.get("data") or {}
    lo, hi = d.get("dealMinPrice"), d.get("dealMaxPrice")
    if lo is None:
        return {"ok": False, "reason": "no_price", "detail": "接口未返回成交价", "raw": d}
    return {"ok": True, "low": float(lo), "high": float(hi or lo),
            "jump_url": d.get("jumpUrl", ""), "raw": d,
            "source": "转转开放平台 market_price"}


def to_residual(keyword: str, creds: Optional[dict] = None) -> Optional[ResidualQuote]:
    """转成 ResidualQuote（残值观测）。失败返回 None，不编造价格。"""
    from datetime import date
    r = query_market_price(keyword, creds=creds)
    if not r.get("ok"):
        return None
    return ResidualQuote(low=r["low"], high=r["high"], kind="market",
                         source=r["source"], observed_at=date.today().isoformat(),
                         confidence="medium", url=r.get("jump_url", ""))


if __name__ == "__main__":
    st = credentials_status()
    print("凭证状态:", json.dumps(st, ensure_ascii=False, indent=1))
    print()
    print("端点契约:")
    for name, spec in ENDPOINTS.items():
        print(f"  {name}: POST {BASE}{spec['path']}")
        print(f"    参数: {', '.join(spec['params'])}")
        print(f"    返回: {'; '.join(f'{k}={v}' for k, v in spec['returns'].items())}")
