from scripts.catalog_git_storage import pack, unpack
import gzip
import pytest
from scripts import catalog_git_storage as storage


def test_git_compression_restores_exact_runtime_bytes(tmp_path):
    raw=b'[{"id":"p", "sources": [], "price":null}]\n'
    (tmp_path/'goods.json').write_bytes(raw)
    pack(tmp_path)
    packed=(tmp_path/'goods.json.gz').read_bytes()
    pack(tmp_path)
    assert (tmp_path/'goods.json.gz').read_bytes()==packed
    (tmp_path/'goods.json').unlink()
    unpack(tmp_path)
    assert (tmp_path/'goods.json').read_bytes()==raw


def test_old_data_branch_still_reads_uncompressed(tmp_path):
    (tmp_path/'goods.json').write_bytes(b'[]')
    unpack(tmp_path)
    assert (tmp_path/'goods.json').read_bytes()==b'[]'


def test_large_category_is_losslessly_stored_and_restored_by_shared_entrypoints(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'SNAPSHOT_THRESHOLD', 100)
    public = tmp_path / 'public'
    public.mkdir()
    (public / 'goods.json').write_bytes(b'[]')
    category = tmp_path / 'data/categories/家电.json'
    category.parent.mkdir(parents=True)
    raw = ('[{"evidence":"完整原始响应' + '证据' * 1000 + '"}]\n').encode()
    category.write_bytes(raw)
    pack(public)
    assert not category.exists()
    packed = category.with_suffix('.json.gz')
    stored = packed.read_bytes()
    assert gzip.decompress(stored) == raw
    unpack(public)
    assert category.read_bytes() == raw
    pack(public)
    assert packed.read_bytes() == stored


def test_category_that_shrinks_removes_its_stale_compressed_copy(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'SNAPSHOT_THRESHOLD', 100)
    category = tmp_path / '家电.json'
    category.write_bytes(b'x' * 1000)
    storage.pack_categories(tmp_path)
    storage.unpack_categories(tmp_path)
    category.write_bytes(b'[]')
    storage.pack_categories(tmp_path)
    assert not category.with_suffix('.json.gz').exists()
    storage.unpack_categories(tmp_path)
    assert category.read_bytes() == b'[]'


def test_oversize_compressed_category_fails_without_deleting_raw_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'SNAPSHOT_THRESHOLD', 1)
    monkeypatch.setattr(storage, 'GIT_BLOB_LIMIT', 1)
    category = tmp_path / '家电.json'
    category.write_bytes(b'original evidence')
    with pytest.raises(ValueError, match='Compressed category exceeds'):
        storage.pack_categories(tmp_path)
    assert category.read_bytes() == b'original evidence'
    assert not category.with_suffix('.json.gz').exists()


def test_corrupt_compressed_category_cannot_replace_existing_runtime_snapshot(tmp_path):
    category = tmp_path / '家电.json'
    category.write_bytes(b'keep evidence')
    category.with_suffix('.json.gz').write_bytes(b'corrupt gzip')
    with pytest.raises(gzip.BadGzipFile):
        storage.unpack_categories(tmp_path)
    assert category.read_bytes() == b'keep evidence'
