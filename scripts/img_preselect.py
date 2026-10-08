"""规格图预筛：在花钱调用视觉之前，用零成本特征挑出候选图。

为什么要这一步（实测的教训）：
  冰箱一个商品有 100 张图（99 张唯一），前 6 张是同一张 5800px 营销长图。
  全跑 = 100 张 × 4 切片 = 400 次视觉调用 ≈ ¥4/台；
  408 台待提取 -> 约 ¥1600 和几十小时。不预筛根本不可行。

规格表的视觉特征（用已验证的空调规格图校准）：
  白底（white > 0.6）  低彩色（colorful < 0.05）  高长宽比（h/w > 1.5）

局限（必须承认）：
  启发式会有漏判/误判，所以：
  - 预筛只做"减少候选"，不做"判定"
  - 每台至少保留 N 张候选（防止全部被筛掉）
  - 记录筛掉了多少，便于事后复核
"""
from __future__ import annotations
import os
import subprocess
from dataclasses import dataclass


@dataclass
class ImgProfile:
    url: str
    width: int = 0
    height: int = 0
    white_ratio: float = 0.0
    colorful_ratio: float = 0.0
    ink_ratio: float = 0.0
    error: str = ""

    @property
    def aspect(self) -> float:
        return (self.height / self.width) if self.width else 0.0


def profile_image(path: str) -> ImgProfile:
    """零成本特征：白底比例 / 彩色比例 / 墨量 / 长宽比

    用纯 PIL 实现（不依赖 numpy —— 本机 Python 3.14 装不上 numpy）。
    """
    from PIL import Image
    try:
        im = Image.open(path).convert("RGB")
    except Exception as e:
        return ImgProfile(url=path, error=str(e))
    w, h = im.size
    # 缩小以加速：宽 300，等比
    tw = 300
    th = max(1, int(h * tw / w))
    im2 = im.resize((tw, th))
    px = list(im2.getdata())
    n = len(px)
    white = colorful = ink = 0
    for r, g, b in px:
        if r > 225 and g > 225 and b > 225:
            white += 1
        mx = r if r > g else g
        if b > mx:
            mx = b
        mn = r if r < g else g
        if b < mn:
            mn = b
        if mx - mn > 40:
            colorful += 1
        if (r + g + b) / 3 < 140:
            ink += 1
    return ImgProfile(url=path, width=w, height=h,
                      white_ratio=white / n, colorful_ratio=colorful / n,
                      ink_ratio=ink / n)


def looks_like_spec(p: ImgProfile) -> bool:
    """是否像规格表（用空调已验证的规格图校准的阈值）"""
    if p.error or not p.width:
        return False
    return (p.white_ratio > 0.6 and p.colorful_ratio < 0.05 and p.aspect > 1.5)


def download(url: str, outdir: str, timeout: int = 30) -> str | None:
    os.makedirs(outdir, exist_ok=True)
    name = os.path.basename(url.split("?")[0]) or "img"
    fp = os.path.join(outdir, name)
    if os.path.exists(fp) and os.path.getsize(fp) > 0:
        return fp
    r = subprocess.run(["curl", "-sS", "-m", str(timeout), "-o", fp, url],
                       capture_output=True)
    if os.path.exists(fp) and os.path.getsize(fp) > 0:
        return fp
    return None


def preselect(imgs: list[dict], outdir: str, min_keep: int = 2,
              max_keep: int = 6, per_tab: int = 2) -> tuple[list[dict], dict]:
    """从候选图中挑出最可能含规格表的，返回 (保留, 统计)

    imgs: [{url, tab_index, part_index, tab_name}]

    关键：**按 tab 分配配额**。实测教训 —— 冰箱有 5 个型号 tab，
    若全局取 top-N，某个 tab 的长图会挤占全部名额，
    导致其他型号的参数完全提取不到（微冰鲜系列只拿到 4 项质保信息）。
    """
    # 去重（同 URL 只留一次）
    seen, uniq = set(), []
    for im in imgs:
        if im["url"] in seen:
            continue
        seen.add(im["url"])
        uniq.append(im)

    scored = []
    for im in uniq:
        fp = download(im["url"], outdir)
        if not fp:
            continue
        pr = profile_image(fp)
        im2 = dict(im)
        im2["local"] = fp
        im2["profile"] = {"white": round(pr.white_ratio, 3),
                          "colorful": round(pr.colorful_ratio, 3),
                          "aspect": round(pr.aspect, 2),
                          "size": f"{pr.width}x{pr.height}"}
        im2["is_spec_like"] = looks_like_spec(pr)
        scored.append(im2)

    # 按 tab 分组，每组内优先取"像规格表"的，再按长宽比降序
    by_tab: dict = {}
    for x in scored:
        by_tab.setdefault(x["tab_index"], []).append(x)

    keep = []
    for ti, group in by_tab.items():
        spec = [x for x in group if x["is_spec_like"]]
        rest = sorted([x for x in group if not x["is_spec_like"]],
                      key=lambda x: -x["profile"]["aspect"])
        picked = (spec + rest)[:per_tab]
        keep += picked
    # 全局上限
    if len(keep) > max_keep:
        keep = keep[:max_keep]
    # 保底
    if len(keep) < min_keep:
        rest = sorted([x for x in scored if x not in keep],
                      key=lambda x: -x["profile"]["aspect"])
        keep += rest[:min_keep - len(keep)]

    stats = {"total": len(imgs), "unique": len(uniq), "profiled": len(scored),
             "kept": len(keep), "dropped": len(scored) - len(keep),
             "tabs": len(by_tab)}
    return keep, stats


if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from vision_params import find_spec_images
    fp = sys.argv[1]
    cat = sys.argv[2] if len(sys.argv) > 2 else "冰箱"
    recs = json.load(open(fp, encoding="utf-8"))
    m = [r for r in recs if (r.get("product") or {}).get("kind") == "machine"]
    for r in m[:2]:
        imgs = find_spec_images(r)
        keep, st = preselect(imgs, "/tmp/gd-prefilter")
        print(f"\n{r['product']['name']}")
        print(f"  {st}")
        for k in keep:
            print(f"    {k['tab_name'][:20]:22s} {k['profile']['size']:>12s} "
                  f"白{k['profile']['white']:.2f} 彩{k['profile']['colorful']:.2f} "
                  f"比{k['profile']['aspect']:.2f}")
