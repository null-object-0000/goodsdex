from scripts.catalog_git_storage import pack, unpack


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
