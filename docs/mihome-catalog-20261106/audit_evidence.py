"""Offline evidence verification: original bytes, directory identity, pagination."""
import hashlib,json,tarfile
from pathlib import Path
root=Path(__file__).resolve().parent
repo=root.parents[1]
manifest=json.loads((repo/'data/official/mihome-catalog.json').read_text())
with tarfile.open(root/'evidence.tar.gz') as archive:
    for entry in manifest['items']:
        raw=archive.extractfile(entry['source_file']).read()
        assert hashlib.sha256(raw).hexdigest()==entry['source_sha256']
        candidates=json.loads(raw)['data']['productList']
        assert any((d['model'],d['pdId'],d['name'])==(entry['model'],entry['pd_id'],entry['name']) for d in candidates)
        icon=entry.get('verified_icon')
        if icon:
            raw=archive.extractfile('raw/icon-'+entry['model']+'.bin').read()
            assert hashlib.sha256(raw).hexdigest()==icon['sha256']
    index={x['file']:x for x in json.loads((root/'requests.json').read_text())}
    for f,record in index.items():
        raw=archive.extractfile(f).read()
        assert hashlib.sha256(raw).hexdigest()==record['sha256']
print('Verified',len(manifest['items']),'identity mappings and',len(index),'original anonymous responses')
