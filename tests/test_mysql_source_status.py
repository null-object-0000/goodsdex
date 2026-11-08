import json
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import source_registry


def test_disabled_workflow_is_paused_without_erasing_its_failure_history(tmp_path,monkeypatch):
    definitions=tmp_path/'definitions.json'
    definitions.write_text(json.dumps([dict(source='all_catalogs',workflow='crawl-all.yml',schedule='paused',period_minutes=1440,note='待修复',last_success=None,consecutive_failures=3)]))
    monkeypatch.setattr(source_registry,'DEFAULT',definitions)
    class API:
        token='test-token'
        def get(self,path):
            if '/runs?' in path:return {'workflow_runs':[dict(id=1,status='completed',conclusion='failure',created_at='2026-11-08T00:00:00Z',updated_at='2026-11-08T00:01:00Z',html_url='https://github.com/example/runs/1')]}
            if path.endswith('/artifacts'):return {'artifacts':[]}
            return {'state':'disabled_manually'}
    row=source_registry.refresh(tmp_path/'state',API(),datetime(2026,11,8,2,tzinfo=timezone.utc))[0]
    assert row['status']=='paused'
    assert row['previous_status']=='failure'
    assert row['consecutive_failures']==1
    assert not row['stale'] and not row['alert']
