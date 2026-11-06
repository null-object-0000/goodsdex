"""Lossless Git storage; runtime and OSS continue to use goods.json verbatim."""
import argparse
import gzip
from pathlib import Path


def unpack(public):
    public = Path(public)
    packed = public / 'goods.json.gz'
    if packed.exists():
        (public / 'goods.json').write_bytes(gzip.decompress(packed.read_bytes()))


def pack(public):
    public = Path(public)
    raw = (public / 'goods.json').read_bytes()
    packed = gzip.compress(raw, compresslevel=6, mtime=0)
    if len(packed) >= 100 * 1024 * 1024:
        raise ValueError('Compressed catalogue exceeds GitHub blob limit')
    (public / 'goods.json.gz').write_bytes(packed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('pack', 'unpack'))
    parser.add_argument('--public', type=Path, required=True)
    args = parser.parse_args()
    (pack if args.action == 'pack' else unpack)(args.public)
