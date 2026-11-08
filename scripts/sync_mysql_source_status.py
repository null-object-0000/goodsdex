"""Refresh lightweight collector status directly in MySQL; never fetch catalogue files."""
import gzip
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, build_opener
from source_registry import refresh
from generate_sources_status import GitHub, NoRedirect


def main():
    base = os.environ['CATALOG_API_URL'].strip().rstrip('/')
    token = os.environ['CATALOG_IMPORT_TOKEN'].strip()
    assert urlparse(base).scheme == 'https' and len(token) >= 32
    endpoint = base + '/admin/api/catalog/status'
    def request(body=None):
        headers = {'Authorization':'Bearer '+token, 'Content-Type':'application/json'}
        wire = None if body is None else gzip.compress(json.dumps(body,ensure_ascii=False).encode(),mtime=0)
        if wire is not None:
            headers['Content-Encoding']='gzip'
        with build_opener(NoRedirect).open(Request(endpoint,data=wire,headers=headers),timeout=60) as response:
            return json.load(response)
    with tempfile.TemporaryDirectory(prefix='source-status-') as directory:
        root = Path(directory)
        saved = root/'data/official/sources-registry.json'
        saved.parent.mkdir(parents=True)
        saved.write_text(json.dumps(request()['registry'],ensure_ascii=False))
        rows = refresh(root,GitHub(os.environ['GITHUB_REPOSITORY'],os.environ['GITHUB_TOKEN']))
        result = request({'registry':rows})
        print(json.dumps({'sources':result['sources'],'paused':sum(r['status']=='paused' for r in rows),'catalogue_payload_bytes':0}))


if __name__ == '__main__':
    main()
