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
    def checkpoint():
        temporary = Path('retired-oss-catalog.json.tmp')
        temporary.write_text(json.dumps({'objects':changed}, ensure_ascii=False))
        temporary.replace('retired-oss-catalog.json')
    # Close the high-volume mutable entry points first, before old immutable blobs.
    primary = [item for item in targets if item[0][len(ROOT):] in ALIASES]
    remaining = [item for item in targets if item not in primary]
    print(json.dumps({'target_objects':len(targets), 'primary_aliases':len(primary)}), flush=True)
    for item in primary:
        row = retire(item)
        changed.append(row)
        checkpoint()
        if 'error_type' in row:
            raise RuntimeError('Primary catalogue ACL update failed; inspect the rollback manifest')
    print('Primary catalogue aliases are private; retiring historical blobs', flush=True)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
    try:
        futures = [executor.submit(retire, item) for item in remaining]
        for future in concurrent.futures.as_completed(futures):
            changed.append(future.result())
            if len(changed) % 100 == 0:
                checkpoint()
            if len(changed) % 500 == 0:
                print(json.dumps({'processed':len(changed), 'total':len(targets)}), flush=True)
    finally:
        checkpoint()
        executor.shutdown(wait=False, cancel_futures=True)
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
