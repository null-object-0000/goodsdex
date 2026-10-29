#!/usr/bin/env python3
"""Compatibility CLI; default dry-run. Shared rules live in goodsdex.dedupe."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from goodsdex.dedupe import *  # noqa: F401,F403
if __name__ == "__main__":
    sys.exit(main())
