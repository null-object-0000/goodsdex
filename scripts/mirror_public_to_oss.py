"""把发布集镜像到 OSS（data/public/），供服务端同步。

为什么需要：大陆机器访问 raw.githubusercontent / jsDelivr / ghproxy 全部不通
（2026-10-27 实测 000 / 403 / 000），服务端改成只从同区域 OSS 拉取。
所以每次定时刷新后必须把 goods.json / meta.json 写到 OSS，否则接口停在旧数据。

用法：python3 scripts/mirror_public_to_oss.py --public _data/public
环境：OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET（GitHub Secrets）
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import sys
import threading
import re
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import oss2

ENDPOINT = 'https://oss-cn-shanghai.aliyuncs.com'
BUCKET = 'spend-good'
PREFIX = 'data/public/'
FILES = ('goods.json', 'meta.json', 'merge-audit.json', 'sources-status.json', 'sources-registry.json')


def object_headers(name, destination, size):
    """Cache content-addressed blobs forever; revalidate live pointers/status."""
    immutable = destination.startswith('blobs/')
    live = destination in ('meta.json', 'sources-status.json', 'sources-registry.json',
                           'prices/latest.json', 'price-history/index.json')
    headers = {'Content-Type': 'application/gzip' if name.endswith('.gz') else 'application/json',
               'Cache-Control': ('public, max-age=31536000, immutable' if immutable else
                                 'no-cache, max-age=0, must-revalidate' if live else
                                 'public, max-age=3600, must-revalidate')}
    if name.endswith(('.json', '.jsonl')) and size >= 1024:
        headers['Content-Encoding'] = 'gzip'
    return headers


def object_matches(head, expected, desired):
    headers = {k.lower(): str(v) for k, v in head.headers.items()}
    wire_md5 = headers.get('x-oss-meta-wire-md5', '')
    wire_bytes = headers.get('x-oss-meta-wire-bytes', '')
    return (headers.get('x-oss-meta-sha256') == expected
            and all(headers.get(k.lower(), '') == v for k, v in desired.items())
            and headers.get('content-encoding', '') == desired.get('Content-Encoding', '')
            and bool(re.fullmatch('[a-f0-9]{32}', wire_md5))
            and headers.get('etag', '').strip('"').lower() == wire_md5
            and wire_bytes.isdigit() and int(wire_bytes) > 0
            and headers.get('content-length') == wire_bytes)


def upload_release(public, uploads, make_bucket, workers=4):
    """Parallelize verified objects; publish meta only after every worker succeeds.

    Each thread owns its OSS client/session. Changed objects retain PUT + GET
    digest checks; verified unchanged aliases also skip payload transfers.
    """
    clients = threading.local()
    def upload(entry):
        name, destination = entry
        if not hasattr(clients, 'bucket'):
            clients.bucket = make_bucket()
        bucket = clients.bucket
        path = public / name
        with path.open('rb') as file:
            expected = hashlib.file_digest(file, 'sha256').hexdigest()
        desired = object_headers(name, destination, path.stat().st_size)
        try:
            if object_matches(bucket.head_object(PREFIX + destination), expected, desired):
                return 0
        except oss2.exceptions.NoSuchKey:
            pass
        local = path.read_bytes()
        wire = gzip.compress(local, compresslevel=6, mtime=0) if desired.get('Content-Encoding') else local
        wire_md5 = hashlib.md5(wire).hexdigest()
        headers = {**desired, 'x-oss-meta-sha256': expected,
                   'x-oss-meta-wire-md5': wire_md5, 'x-oss-meta-wire-bytes': str(len(wire)),
                   'Content-MD5': base64.b64encode(bytes.fromhex(wire_md5)).decode()}
        with tempfile.TemporaryDirectory(prefix='oss-wire-') as folder:
            upload_path = Path(folder) / 'object'
            upload_path.write_bytes(wire)
            result = bucket.put_object_from_file(PREFIX + destination, str(upload_path), headers=headers)
        if result.status != 200:
            raise RuntimeError(f'OSS upload failed: {destination} HTTP {result.status}')
        remote = bucket.get_object(PREFIX + destination).read()
        # oss2 normally decodes Content-Encoding through requests.iter_content.
        # Also support transports exposing the compressed representation verbatim.
        if desired.get('Content-Encoding') and remote.startswith(b'\x1f\x8b'):
            remote = gzip.decompress(remote)
        if hashlib.sha256(remote).hexdigest() != expected:
            raise RuntimeError(f'OSS readback mismatch: {destination}')
        print(f'OSS GET verified {destination}: bytes={len(local)} wire_bytes={len(wire)} sha256={expected}')
        return 1
    objects = [(name, destination) for name, destination in uploads if destination not in ('meta.json', 'price-history/index.json')]
    manifest = [(name, destination) for name, destination in uploads if destination == 'meta.json']
    if len(manifest) != 1:
        raise ValueError('Exactly one final manifest is required')
    with ThreadPoolExecutor(max_workers=workers) as pool:
        uploaded = sum(pool.map(upload, objects))
    for entry in uploads:
        if entry[1] == 'price-history/index.json':
            uploaded += upload(entry)
    # No worker can still be uploading, and every readback has passed.
    return uploaded + upload(manifest[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--public', required=True)
    ap.add_argument('--bucket', default=BUCKET)
    args = ap.parse_args()

    key_id = os.environ.get('OSS_ACCESS_KEY_ID', '').strip()
    key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET', '').strip()
    if not key_id or not key_secret:
        print('缺少 OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET', file=sys.stderr)
        return 2

    with open(os.path.join(args.public, 'merge-audit.json')) as fp:
        audit = json.load(fp)['deduplication']
    with open(os.path.join(args.public, 'goods.json'), 'rb') as fp:
        goods = fp.read()
    if hashlib.sha256(goods).hexdigest() != audit['output_sha256']:
        raise ValueError('Goods changed after final merge validation')
    from pathlib import Path
    public = Path(args.public)
    meta = json.loads((public / 'meta.json').read_bytes())
    descriptors = {**meta.get('files', {}), **meta.get('price_history', {}).get('files', {})}
    if meta.get('schema') != 1 or not descriptors:
        raise ValueError('Run finalize_public.py to generate sharded release first')
    if 'revision' in meta:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
        from goodsdex.exclusions import validate_excluded
        if 'goods-excluded.json' not in descriptors:
            raise ValueError('Missing exclusion descriptor')
        validate_excluded(meta, json.loads((public / 'goods-excluded.json').read_bytes()), json.loads(goods))
    # Verify every file before touching OSS; the manifest is the last commit marker.
    for name, descriptor in descriptors.items():
        raw = (public / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != descriptor['sha256'] or len(raw) != descriptor['bytes']:
            raise ValueError(f'Shard changed after generation: {name}')
    uploads = [(name, f"blobs/{d['sha256']}.json") for name, d in descriptors.items()]
    uploads += [(name, name) for name in descriptors if name != 'goods.json']
    uploads += [('goods.json', 'goods.json'), ('merge-audit.json', 'merge-audit.json'), ('meta.json', 'meta.json')]
    uploaded = upload_release(public, uploads,
        lambda: oss2.Bucket(oss2.Auth(key_id, key_secret), ENDPOINT, args.bucket))
    if not uploaded:
        print('OSS mirror already verified and current; no object payload transferred')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
