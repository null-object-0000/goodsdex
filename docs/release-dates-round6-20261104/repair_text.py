"""Decode HTTP content encoding without changing captured response bytes or hashes."""
import gzip,json
from capture import ROOT,Text
for f in (ROOT/'evidence').glob('*.json'):
 o=json.loads(f.read_text());raw=gzip.decompress(__import__('pathlib').Path(o['raw_file']).read_bytes());decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
 p=Text();p.feed(decoded.decode('utf-8','replace'));o['text']=' '.join(' '.join(p.parts).split());f.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
