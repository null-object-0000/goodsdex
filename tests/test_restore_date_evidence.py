import pytest
from restore_date_evidence import restore, validate_run


def test_evidence_restore_refuses_product_or_executable_payloads(tmp_path):
    src=tmp_path/'source';out=tmp_path/'out';src.mkdir();out.mkdir()
    (src/'goods.json').write_text('[]')
    with pytest.raises(ValueError,match='Unexpected'):restore(src,out)
    (src/'goods.json').unlink();p=src/'data/official/hp-release-evidence.json';p.parent.mkdir(parents=True);p.write_text('{"captured_at":"2026-11-16T00:00:00Z"}')
    assert restore(src,out)==1
    assert (out/'data/official/hp-release-evidence.json').read_text()==p.read_text()


def test_replay_requires_original_successful_trusted_collection():
    class API:
        def get(self,path):
            if path.endswith('?per_page=100'):return {'jobs':[{'name':'collect','conclusion':'success'}]}
            return {'path':'.github/workflows/release-dates-daily.yml','head_branch':'main','event':'workflow_dispatch'}
    validate_run('123',API())
    with pytest.raises(ValueError):validate_run('../123',API())
    class Failed(API):
        def get(self,path):
            return {'jobs':[{'name':'collect','conclusion':'failure'}]} if path.endswith('?per_page=100') else super().get(path)
    with pytest.raises(ValueError):validate_run('123',Failed())


def test_replay_restores_recorded_capture_subdirectories(tmp_path):
    src=tmp_path/'source';p=src/'data/third-party/l5-captures/fingerprint.html.gz';p.parent.mkdir(parents=True);p.write_bytes(b'captured response')
    root=tmp_path/'root';root.mkdir()
    assert restore(src,root)==1
    assert (root/'data/third-party/l5-captures/fingerprint.html.gz').read_bytes()==b'captured response'
