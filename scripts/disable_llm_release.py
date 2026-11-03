"""One switch rollback: disable the separate LLM input, preserve official data.

Run finalization and the normal publication workflow afterwards to update live data.
"""
import json
from pathlib import Path

if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'data/llm/release-dates.json'
    bundle = json.loads(path.read_text())
    bundle['enabled'] = False
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + '\n')
    print('LLM sidecar disabled; official input unchanged. Finalize and publish to apply.')
