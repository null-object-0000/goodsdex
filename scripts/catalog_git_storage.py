"""Lossless Git storage; runtime and OSS continue to use goods.json verbatim."""
import argparse
import gzip
from pathlib import Path

SNAPSHOT_THRESHOLD = 50 * 1024 * 1024
GIT_BLOB_LIMIT = 100 * 1024 * 1024


def pack_categories(categories):
    """Store large evidence snapshots as deterministic, lossless gzip blobs."""
    for path in Path(categories).glob('*.json'):
        packed_path = path.with_suffix('.json.gz')
        if path.stat().st_size < SNAPSHOT_THRESHOLD:
            packed_path.unlink(missing_ok=True)
            continue
        raw = path.read_bytes()
        compressed = gzip.compress(raw, compresslevel=6, mtime=0)
        if len(compressed) >= GIT_BLOB_LIMIT:
            raise ValueError(f'Compressed category exceeds GitHub blob limit: {path.name}')
        temporary = packed_path.with_suffix('.gz.tmp')
        temporary.write_bytes(compressed)
        temporary.replace(packed_path)
        path.unlink()


def unpack_categories(categories):
    for path in Path(categories).glob('*.json.gz'):
        # Decompress and validate CRC before touching a restored snapshot.
        raw = gzip.decompress(path.read_bytes())
        path.with_suffix('').write_bytes(raw)


def unpack(public):
    public = Path(public)
    packed = public / 'goods.json.gz'
    if packed.exists():
        (public / 'goods.json').write_bytes(gzip.decompress(packed.read_bytes()))
    unpack_categories(public.parent / 'data/categories')


def pack(public):
    public = Path(public)
    raw = (public / 'goods.json').read_bytes()
    packed = gzip.compress(raw, compresslevel=6, mtime=0)
    if len(packed) >= GIT_BLOB_LIMIT:
        raise ValueError('Compressed catalogue exceeds GitHub blob limit')
    (public / 'goods.json.gz').write_bytes(packed)
    pack_categories(public.parent / 'data/categories')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('pack', 'unpack'))
    parser.add_argument('--public', type=Path, required=True)
    args = parser.parse_args()
    (pack if args.action == 'pack' else unpack)(args.public)
