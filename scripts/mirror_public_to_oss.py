"""把发布集镜像到 OSS（data/public/），供服务端同步。

为什么需要：大陆机器访问 raw.githubusercontent / jsDelivr / ghproxy 全部不通
（2026-10-27 实测 000 / 403 / 000），服务端改成只从同区域 OSS 拉取。
所以每次定时刷新后必须把 goods.json / meta.json 写到 OSS，否则接口停在旧数据。

用法：python3 scripts/mirror_public_to_oss.py --public _data/public
环境：OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET（GitHub Secrets）
"""
import argparse
import hashlib
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import oss2

ENDPOINT = 'https://oss-cn-shanghai.aliyuncs.com'
BUCKET = 'spend-good'
PREFIX = 'data/public/'
FILES = ('goods.json', 'meta.json', 'merge-audit.json')


def upload_release(public, uploads, make_bucket, workers=4):
    """Parallelize verified objects; publish meta only after every worker succeeds.

    Each thread owns its OSS client/session. Immutable blobs and aliases retain
    their PUT + GET digest checks; failures leave the manifest unpublished.
    """
    clients = threading.local()
    def upload(entry):
        name, destination = entry
        if not hasattr(clients, 'bucket'):
            clients.bucket = make_bucket()
        bucket = clients.bucket
        path = public / name
        local = path.read_bytes()
        expected = hashlib.sha256(local).hexdigest()
        if destination.startswith('blobs/'):
            try:
                head = bucket.head_object(PREFIX + destination)
                if head.headers.get('x-oss-meta-sha256') == expected:
                    return 0
            except oss2.exceptions.NoSuchKey:
                pass
        result = bucket.put_object_from_file(PREFIX + destination, str(path),
            headers={'Content-Type': 'application/json', 'x-oss-meta-sha256': expected})
        if result.status != 200:
            raise RuntimeError(f'OSS upload failed: {destination} HTTP {result.status}')
        remote = bucket.get_object(PREFIX + destination).read()
        if hashlib.sha256(remote).hexdigest() != expected:
            raise RuntimeError(f'OSS readback mismatch: {destination}')
        print(f'OSS GET verified {destination}: bytes={len(local)} sha256={expected}')
        return 1
    objects = [(name, destination) for name, destination in uploads if destination != 'meta.json']
    manifest = [(name, destination) for name, destination in uploads if destination == 'meta.json']
    if len(manifest) != 1:
        raise ValueError('Exactly one final manifest is required')
    with ThreadPoolExecutor(max_workers=workers) as pool:
        uploaded = sum(pool.map(upload, objects))
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
    descriptors = meta.get('files', {})
    if meta.get('schema') != 1 or not descriptors:
        raise ValueError('Run finalize_public.py to generate sharded release first')
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
        print('没有任何文件被镜像，判定为失败', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
