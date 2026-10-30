"""Upload only the two reviewed Han 2022 archive JPEGs; verify public URL bytes."""
import hashlib
import io
import json
import os
from pathlib import Path
import urllib.request
import oss2
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/汉2022官方存档图-20261030'
BASE = 'https://spend-good.oss-cn-shanghai.aliyuncs.com/'


def main():
    rows = json.loads((EVIDENCE / 'images.json').read_text())
    assert [r['name'] for r in rows] == ['H1', 'H2']
    checked = []
    for row, dimensions in zip(rows, [(780, 440), (1920, 550)]):
        raw = (EVIDENCE / (row['name'] + '.jpg')).read_bytes()
        assert len(raw) == row['bytes'] > 30000
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        image = Image.open(io.BytesIO(raw))
        assert image.format == 'JPEG' and image.size == dimensions
        assert row['key'] == 'goods/' + hashlib.sha1(row['source_url'].encode()).hexdigest() + '.jpg'
        checked.append((row, raw))
    bucket = oss2.Bucket(oss2.Auth(os.environ['OSS_ACCESS_KEY_ID'], os.environ['OSS_ACCESS_KEY_SECRET']),
                         'https://oss-cn-shanghai.aliyuncs.com', 'spend-good')
    for row, raw in checked:
        result = bucket.put_object(row['key'], raw, headers={'Content-Type': 'image/jpeg',
            'x-oss-object-acl': 'public-read', 'Cache-Control': 'public,max-age=31536000,immutable'})
        assert result.status == 200
        url = BASE + row['key']
        with urllib.request.urlopen(url, timeout=60) as response:
            remote = response.read()
            assert response.status == 200 and remote == raw
        print(json.dumps(dict(name=row['name'], url=url, status=200, bytes=len(remote), sha256=row['sha256'])))


if __name__ == '__main__':
    main()
