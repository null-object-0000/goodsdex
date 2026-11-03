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
    # Every manifest hash is validated before the upload function can run.
    (tmp_path/'sources-status.json').write_bytes(b'changed after manifest')
    with pytest.raises(ValueError, match='changed after generation'):
        mirror.main()
