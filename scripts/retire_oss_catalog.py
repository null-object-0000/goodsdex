"""Retain catalogue rollback objects privately, without downloading any payloads."""
import concurrent.futures
import json
import os
from pathlib import Path
import urllib.request

ROOT = 'data/public/'
ALIASES = {'goods.json', 'goods.json.gz', 'goods-excluded.json', 'meta.json',
           'sources-status.json', 'sources-registry.json', 'release-coverage.json'}


def is_catalogue(key):
    if not key.startswith(ROOT):
        return False
    name = key[len(ROOT):]
    return name in ALIASES or (name.startswith(('blobs/', 'index/', 'detail/', 'prices/'))
                              and name.endswith(('.json', '.json.gz', '.jsonl', '.jsonl.gz')))


def main():
    import oss2
    expected = os.environ['EXPECTED_API_COMMIT']
    assert len(expected) == 40 and all(c in '0123456789abcdef' for c in expected)
    def api(name):
        with urllib.request.urlopen('https://spend.snewbie.site/' + name, timeout=15) as r:
            return json.load(r)
    assert api('health.json')['gitCommit'] == expected, 'API deployment is not the expected version'
    meta = api('api/meta')
    assert meta['storage'] == 'mysql' and meta['count'] > 4000, 'MySQL cutover is not ready'
    bucket = oss2.Bucket(oss2.Auth(os.environ['OSS_ACCESS_KEY_ID'], os.environ['OSS_ACCESS_KEY_SECRET']),
                         'https://oss-cn-shanghai.aliyuncs.com', 'spend-good')
    targets = [(o.key, o.size) for o in oss2.ObjectIteratorV2(bucket, prefix=ROOT) if is_catalogue(o.key)]
    assert any(k == ROOT + 'goods.json' for k, _ in targets), 'Expected legacy catalogue missing'
    changed = []
    def retire(item):
        key, size = item
        try:
            before = bucket.get_object_acl(key).acl
            if before != oss2.OBJECT_ACL_PRIVATE:
                bucket.put_object_acl(key, oss2.OBJECT_ACL_PRIVATE)
            return {'key':key, 'bytes':size, 'previous_acl':before}
        except Exception as error:
            return {'key':key, 'bytes':size, 'error_type':type(error).__name__}
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            for row in executor.map(retire, targets):
                changed.append(row)
    finally:
        Path('retired-oss-catalog.json').write_text(json.dumps({'objects':changed}, ensure_ascii=False))
    failures = sum('error_type' in row for row in changed)
    if failures:
        raise RuntimeError(f'{failures} ACL operations failed; inspect the private rollback manifest')
    for key in [ROOT + 'goods.json', ROOT + 'meta.json']:
        assert bucket.get_object_acl(key).acl == oss2.OBJECT_ACL_PRIVATE
        try:
            urllib.request.urlopen(urllib.request.Request('https://spend-good.oss-cn-shanghai.aliyuncs.com/' + key, method='HEAD'), timeout=15)
            raise AssertionError('Anonymous catalogue access is still enabled')
        except urllib.error.HTTPError as error:
            assert error.code == 403
    # Image ACLs are never changed by this operation.
    print(json.dumps({'private_backup_objects':len(changed), 'stored_bytes':sum(r['bytes'] for r in changed),
                      'downloaded_object_payload_bytes':0, 'api_commit':expected}))


if __name__ == '__main__':
    main()
