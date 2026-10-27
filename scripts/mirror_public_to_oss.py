"""把发布集镜像到 OSS（data/public/），供服务端同步。

为什么需要：大陆机器访问 raw.githubusercontent / jsDelivr / ghproxy 全部不通
（2026-10-27 实测 000 / 403 / 000），服务端改成只从同区域 OSS 拉取。
所以每次定时刷新后必须把 goods.json / meta.json 写到 OSS，否则接口停在旧数据。

用法：python3 scripts/mirror_public_to_oss.py --public _data/public
环境：OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET（GitHub Secrets）
"""
import argparse
import os
import sys

import oss2

ENDPOINT = 'https://oss-cn-shanghai.aliyuncs.com'
BUCKET = 'spend-good'
PREFIX = 'data/public/'
FILES = ('goods.json', 'meta.json')


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

    bucket = oss2.Bucket(oss2.Auth(key_id, key_secret), ENDPOINT, args.bucket)
    uploaded = 0
    for name in FILES:
        path = os.path.join(args.public, name)
        if not os.path.exists(path):
            print(f'跳过（不存在）{name}')
            continue
        result = bucket.put_object_from_file(
            PREFIX + name, path, headers={'Content-Type': 'application/json'})
        print(f'已镜像 {name} {os.path.getsize(path)} 字节 HTTP {result.status}')
        uploaded += 1
    if not uploaded:
        print('没有任何文件被镜像，判定为失败', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
