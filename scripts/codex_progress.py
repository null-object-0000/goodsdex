"""读 Codex session transcript 的进展（技能里说明的方法）。

用法:
  python3 scripts/codex_progress.py                # 最新 session
  python3 scripts/codex_progress.py <sessionid前缀>
  python3 scripts/codex_progress.py --tail 30
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

SESS = Path(os.path.expanduser("~/.codex/sessions"))


def newest_session(prefix: str = "") -> Path | None:
    files = sorted(glob.glob(str(SESS / "*/*/*/*.jsonl")), key=os.path.getmtime,
                   reverse=True)
    for f in files:
        if not prefix or prefix in os.path.basename(f):
            return Path(f)
    return None


def parse(fp: Path) -> list[dict]:
    out = []
    for line in fp.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
        except Exception:
            continue
        out.append(j)
    return out


def summarize(events: list[dict], tail: int = 20) -> None:
    items = []
    for e in events:
        payload = e.get("payload") or {}
        typ = payload.get("type") or e.get("type")
        if typ == "function_call" or "command" in str(payload.get("name", "")).lower():
            args = payload.get("arguments") or ""
            try:
                a = json.loads(args) if isinstance(args, str) else args
                cmd = (a or {}).get("command") or (a or {}).get("cmd") or args
            except Exception:
                cmd = args
            items.append(("CMD", str(cmd)[:160]))
        elif typ == "function_call_output":
            out = payload.get("output") or ""
            if isinstance(out, dict):
                out = json.dumps(out, ensure_ascii=False)
            items.append(("OUT", str(out)[:200].replace("\n", " ")))
        elif typ == "agent_message" or payload.get("role") == "assistant":
            txt = payload.get("message") or payload.get("content") or ""
            if isinstance(txt, list):
                txt = " ".join(str(x) for x in txt)
            if str(txt).strip():
                items.append(("MSG", str(txt)[:400].replace("\n", " ")))
        elif typ in ("reasoning", "agent_reasoning"):
            txt = payload.get("text") or payload.get("summary") or ""
            if isinstance(txt, list):
                txt = " ".join(str(x) for x in txt)
            if str(txt).strip():
                items.append(("THINK", str(txt)[:250].replace("\n", " ")))

    print(f"事件 {len(items)} 条，显示最后 {tail} 条：\n")
    for kind, txt in items[-tail:]:
        icon = {"CMD": "🔧", "OUT": "  ↳", "MSG": "💬", "THINK": "·"}.get(kind, "?")
        print(f"{icon} {txt}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("session", nargs="?", default="")
    ap.add_argument("--tail", type=int, default=20)
    a = ap.parse_args()
    fp = newest_session(a.session)
    if not fp:
        print("没找到 session 文件")
        return 1
    print(f"session: {fp.name}\n")
    summarize(parse(fp), a.tail)
    # 检查进程是否还活着
    p = subprocess.run(["pgrep", "-af", "codex exec"], capture_output=True, text=True)
    print(f"\nCodex 进程: {'运行中' if p.stdout.strip() else '已退出'}")
    if p.stdout.strip():
        print("  " + p.stdout.strip()[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
