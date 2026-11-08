"""Publication marker must follow successful readback of every parallel object."""
import importlib.util
import io
from pathlib import Path
import sys
import threading
import types

import pytest


@pytest.fixture
def mirror(monkeypatch):
    fake = types.SimpleNamespace(exceptions=types.SimpleNamespace(NoSuchKey=KeyError))
    monkeypatch.setitem(sys.modules, 'oss2', fake)
    spec = importlib.util.spec_from_file_location('mirror', Path(__file__).resolve().parents[1]/'scripts/mirror_public_to_oss.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_waits_for_all_verified_objects_and_clients_are_thread_local(tmp_path, mirror):
    events, store, owners = [], {}, {}
    lock = threading.Lock()
    class Bucket:
        def __init__(self):
            self.owner = threading.get_ident()
            owners[id(self)] = self.owner
        def head_object(self, destination):
            raise KeyError(destination)
        def put_object_from_file(self, destination, path, headers):
            assert self.owner == threading.get_ident()
            with lock:
                events.append(('put', destination))
                store[destination] = Path(path).read_bytes()
            return types.SimpleNamespace(status=200)
        def get_object(self, destination):
            assert self.owner == threading.get_ident()
            with lock:
                events.append(('verified', destination))
            return io.BytesIO(store[destination])
    names = [f'{i}.json' for i in range(8)] + ['meta.json']
    for name in names:
        (tmp_path/name).write_text(name)
    assert mirror.upload_release(tmp_path, [(name,name) for name in names], Bucket) == len(names)
    assert events[-2:] == [('put', mirror.PREFIX+'meta.json'), ('verified', mirror.PREFIX+'meta.json')]
    assert len([e for e in events[:-2] if e[0] == 'verified']) == 8


def test_failed_readback_does_not_publish_manifest(tmp_path, mirror):
    puts = []
    class Bucket:
        def head_object(self, destination):
            raise KeyError(destination)
        def put_object_from_file(self, destination, path, headers):
            puts.append(destination)
            return types.SimpleNamespace(status=200)
        def get_object(self, destination):
            return io.BytesIO(b'corrupt remote object')
    for name in ('goods.json','meta.json'):
        (tmp_path/name).write_text('expected')
    with pytest.raises(RuntimeError, match='readback mismatch'):
        mirror.upload_release(tmp_path, [(name,name) for name in ('goods.json','meta.json')], Bucket)
    assert mirror.PREFIX+'meta.json' not in puts


def test_status_manifest_descriptor_drives_blob_and_public_alias(tmp_path, mirror, monkeypatch):
    import hashlib
    import json
    goods, status = b'[]', b'{"sources":[]}'
    (tmp_path/'goods.json').write_bytes(goods)
    (tmp_path/'sources-status.json').write_bytes(status)
    (tmp_path/'merge-audit.json').write_text(json.dumps({'deduplication': {'output_sha256': hashlib.sha256(goods).hexdigest()}}))
    descriptors = {name: dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
                   for name, raw in [('goods.json', goods), ('sources-status.json', status)]}
    (tmp_path/'meta.json').write_text(json.dumps(dict(schema=1, files=descriptors)))
    captured = []
    def upload(public, uploads, make_bucket):
        captured.extend(uploads)
        return len(uploads)
    monkeypatch.setattr(mirror, 'upload_release', upload)
    monkeypatch.setenv('OSS_ACCESS_KEY_ID', 'test')
    monkeypatch.setenv('OSS_ACCESS_KEY_SECRET', 'test')
    monkeypatch.setattr(sys, 'argv', ['mirror', '--public', str(tmp_path)])
    assert mirror.main() == 0
    digest = hashlib.sha256(status).hexdigest()
    assert ('sources-status.json', f'blobs/{digest}.json') in captured
    assert ('sources-status.json', 'sources-status.json') in captured
    monkeypatch.setattr(mirror, 'upload_release', lambda public, uploads, make_bucket: 0)
    assert mirror.main() == 0  # A verified no-op must not trigger retries/publication alerts.
    # Every manifest hash is validated before the upload function can run.
    (tmp_path/'sources-status.json').write_bytes(b'changed after manifest')
    with pytest.raises(ValueError, match='changed after generation'):
        mirror.main()


def test_exclusion_file_is_mirrored_and_stale_release_fails_before_upload(tmp_path, mirror, monkeypatch):
    import json
    from goodsdex.dedupe import finalize_public
    from goodsdex.shards import build_shards
    (tmp_path/'goods.json').write_text('[]')
    finalize_public(tmp_path)
    meta = build_shards(tmp_path)
    uploads_seen = []
    monkeypatch.setattr(mirror, 'upload_release', lambda public, uploads, make_bucket: uploads_seen.extend(uploads) or len(uploads))
    monkeypatch.setenv('OSS_ACCESS_KEY_ID', 'test')
    monkeypatch.setenv('OSS_ACCESS_KEY_SECRET', 'test')
    monkeypatch.setattr(sys, 'argv', ['mirror', '--public', str(tmp_path)])
    assert mirror.main() == 0
    assert ('goods-excluded.json', 'goods-excluded.json') in uploads_seen
    assert ('goods-excluded.json', f"blobs/{meta['files']['goods-excluded.json']['sha256']}.json") in uploads_seen
    excluded = json.loads((tmp_path/'goods-excluded.json').read_text())
    excluded['revision'] = 'stale'
    (tmp_path/'goods-excluded.json').write_text(json.dumps(excluded))
    uploads_seen.clear()
    with pytest.raises(ValueError, match='another release'):
        mirror.main()
    assert not uploads_seen


def test_history_index_follows_month_readback_and_precedes_meta(tmp_path, mirror):
    names = ['price-history/2026-11.jsonl.gz', 'price-history/index.json', 'meta.json']
    store, events = {}, []
    for name in names:
        path = tmp_path/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(name.encode())
    class Bucket:
        def head_object(self, destination):
            raise KeyError(destination)
        def put_object_from_file(self, destination, path, headers):
            store[destination] = Path(path).read_bytes()
            events.append(('put', destination))
            if destination.endswith('.gz'):
                assert headers['Content-Type'] == 'application/gzip'
            return types.SimpleNamespace(status=200)
        def get_object(self, destination):
            events.append(('verified', destination))
            return io.BytesIO(store[destination])
    assert mirror.upload_release(tmp_path, [(n,n) for n in reversed(names)], Bucket) == 3
    assert events == [(action, mirror.PREFIX+name) for name in names for action in ('put','verified')]


def test_separate_history_descriptors_are_mirrored(tmp_path, mirror, monkeypatch):
    import hashlib
    import json
    raw = {'goods.json': b'[]', 'price-history/index.json': b'{}', 'price-history/2026-11.jsonl.gz': b'gzip bytes'}
    descriptors = {}
    for name, content in raw.items():
        path=tmp_path/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(content)
        descriptors[name] = dict(sha256=hashlib.sha256(content).hexdigest(),bytes=len(content),count=1)
    (tmp_path/'meta.json').write_text(json.dumps(dict(schema=1,files={'goods.json':descriptors.pop('goods.json')},price_history={'files':descriptors})))
    (tmp_path/'merge-audit.json').write_text(json.dumps({'deduplication':{'output_sha256':hashlib.sha256(raw['goods.json']).hexdigest()}}))
    captured=[]
    monkeypatch.setattr(mirror,'upload_release',lambda public,uploads,make_bucket:captured.extend(uploads) or len(uploads))
    monkeypatch.setenv('OSS_ACCESS_KEY_ID','test'); monkeypatch.setenv('OSS_ACCESS_KEY_SECRET','test')
    monkeypatch.setattr(sys,'argv',['mirror','--public',str(tmp_path)])
    assert mirror.main()==0
    assert ('price-history/index.json','price-history/index.json') in captured
    assert ('price-history/2026-11.jsonl.gz','price-history/2026-11.jsonl.gz') in captured


@pytest.mark.parametrize('sdk_decodes_gzip', [False, True])
def test_unchanged_aliases_and_blobs_transfer_no_payload_after_verified_compressed_upload(tmp_path, mirror, sdk_decodes_gzip):
    import gzip
    import hashlib
    import base64
    store, metadata, events = {}, {}, []
    class Bucket:
        def head_object(self, destination):
            if destination not in store:
                raise KeyError(destination)
            return types.SimpleNamespace(headers=metadata[destination])
        def put_object_from_file(self, destination, path, headers):
            wire = Path(path).read_bytes()
            assert headers['Content-MD5'] == base64.b64encode(hashlib.md5(wire).digest()).decode()
            store[destination] = wire
            metadata[destination] = {k.lower(): v for k, v in headers.items()}
            metadata[destination].update({'etag': '"'+hashlib.md5(wire).hexdigest().upper()+'"',
                                          'content-length': str(len(wire))})
            events.append(('put', destination))
            return types.SimpleNamespace(status=200)
        def get_object(self, destination):
            events.append(('get', destination))
            wire = store[destination]
            if sdk_decodes_gzip and metadata[destination].get('content-encoding') == 'gzip':
                wire = gzip.decompress(wire)
            return io.BytesIO(wire)
    raw = b'[{"name":"repeated product evidence"}]\n' * 1000
    (tmp_path/'goods.json').write_bytes(raw)
    (tmp_path/'meta.json').write_bytes(b'{"revision":1}')
    blob = 'blobs/'+hashlib.sha256(raw).hexdigest()+'.json'
    uploads = [('goods.json','goods.json'), ('goods.json',blob), ('meta.json','meta.json')]
    assert mirror.upload_release(tmp_path, uploads, Bucket) == 3
    assert gzip.decompress(store[mirror.PREFIX+'goods.json']) == raw
    assert len(store[mirror.PREFIX+'goods.json']) < len(raw) / 10
    assert metadata[mirror.PREFIX+blob]['cache-control'] == 'public, max-age=31536000, immutable'
    assert metadata[mirror.PREFIX+'goods.json']['cache-control'] == 'public, max-age=3600, must-revalidate'
    assert metadata[mirror.PREFIX+'meta.json']['cache-control'] == 'no-cache, max-age=0, must-revalidate'
    assert events[-2:] == [('put',mirror.PREFIX+'meta.json'), ('get',mirror.PREFIX+'meta.json')]
    events.clear()
    assert mirror.upload_release(tmp_path, uploads, Bucket) == 0
    assert events == []
    (tmp_path/'meta.json').write_bytes(b'{"revision":2}')
    assert mirror.upload_release(tmp_path, uploads, Bucket) == 1
    assert events == [('put',mirror.PREFIX+'meta.json'), ('get',mirror.PREFIX+'meta.json')]


def test_cached_sha_alone_cannot_skip_wire_or_cache_header_migration(tmp_path, mirror):
    import hashlib
    raw = b'{}'
    (tmp_path/'meta.json').write_bytes(raw)
    puts = []
    class Bucket:
        def head_object(self, destination):
            return types.SimpleNamespace(headers={'x-oss-meta-sha256': hashlib.sha256(raw).hexdigest()})
        def put_object_from_file(self, destination, path, headers):
            puts.append(destination)
            return types.SimpleNamespace(status=200)
        def get_object(self, destination):
            return io.BytesIO(raw)
    assert mirror.upload_release(tmp_path, [('meta.json','meta.json')], Bucket) == 1
    assert puts == [mirror.PREFIX+'meta.json']


def test_precompressed_history_is_never_double_encoded(tmp_path, mirror):
    import gzip
    raw = gzip.compress(b'[{"price":10}]', mtime=0)
    (tmp_path/'history.jsonl.gz').write_bytes(raw)
    (tmp_path/'meta.json').write_bytes(b'{}')
    store = {}
    class Bucket:
        def head_object(self, destination):
            raise KeyError(destination)
        def put_object_from_file(self, destination, path, headers):
            store[destination] = Path(path).read_bytes()
            if destination.endswith('history.jsonl.gz'):
                assert headers['Content-Type'] == 'application/gzip'
                assert 'Content-Encoding' not in headers
            return types.SimpleNamespace(status=200)
        def get_object(self, destination):
            return io.BytesIO(store[destination])
    mirror.upload_release(tmp_path, [('history.jsonl.gz','history.jsonl.gz'),('meta.json','meta.json')], Bucket)
    assert store[mirror.PREFIX+'history.jsonl.gz'] == raw
