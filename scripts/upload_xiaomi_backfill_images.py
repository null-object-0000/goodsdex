"""Transfer fixed reviewed URLs to OSS; failed readback never enters the patch set."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import threading
from urllib.parse import urlsplit
import hashlib
import io
import json
import os
from pathlib import Path
import time
import urllib.request
from PIL import Image

BASE='https://spend-good.oss-cn-shanghai.aliyuncs.com/'

def transfer(row, bucket, download):
    ext={'image/jpeg':'jpg','image/png':'png'}[row['content_type']]
    assert row['key']=='goods/'+hashlib.sha1(row['image_url'].encode()).hexdigest()+'.'+ext
    assert all(row.get(k) for k in ('source','source_url','captured_at','captured_at_kind'))
    raw=download(row['image_url'])
    assert len(raw)==row['bytes'], 'candidate_bytes_changed'
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        assert im.width==row['width']>=600 and im.height==row['height'], 'candidate_dimensions_changed'
        assert im.format=={'jpg':'JPEG','png':'PNG'}[ext], 'format_changed'
    # Preserve bytes locally before uploading, without any transformation.
    local=Path('image-transfer-cache')/Path(row['key']).name
    local.parent.mkdir(exist_ok=True);local.write_bytes(raw)
    existed=bucket.object_exists(row['key'])
    if existed:
        assert bucket.get_object(row['key']).read()==raw, 'existing_oss_object_conflict'
    else:
        result=bucket.put_object_from_file(row['key'],str(local),headers={
            'Content-Type':row['content_type'],'x-oss-object-acl':'public-read',
            'Cache-Control':'public,max-age=31536000,immutable'})
        if result.status!=200:
            bucket.delete_object(row['key'])
            raise ValueError('upload_failed')
    try:
        remote=download(BASE+row['key'])
        assert remote==local.read_bytes(), 'oss_public_readback_mismatch'
    except Exception:
        if not existed:bucket.delete_object(row['key'])
        raise
    return dict(row,oss_url=BASE+row['key'],http_status=200,readback_bytes=len(remote),
        sha256=hashlib.sha256(raw).hexdigest(),byte_equal=True,preexisting_object=existed)

def main():
    import oss2
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    bucket=oss2.Bucket(oss2.Auth(os.environ['OSS_ACCESS_KEY_ID'],os.environ['OSS_ACCESS_KEY_SECRET']),
        'https://oss-cn-shanghai.aliyuncs.com','spend-good')
    locks=defaultdict(threading.Lock)
    last_request=defaultdict(float)
    def download(url):
        host=urlsplit(url).hostname
        if host != urlsplit(BASE).hostname:
            with locks[host]:
                time.sleep(max(0,2.1-(time.monotonic()-last_request[host])))
                last_request[host]=time.monotonic()
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:
            assert r.status==200, 'get_not_200'
            return r.read()
    manifest=json.loads(a.manifest.read_text())
    groups=defaultdict(list)
    for row in manifest:groups[row['key']].append(row)
    results=[];skipped=[]
    a.out.mkdir(parents=True,exist_ok=True)
    def checkpoint():
        for name,obj in [('oss-readback.json',results),('skipped-transfer.json',skipped)]:
            (a.out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    # Each object has exactly one worker, even when several product IDs share it.
    # Separate clients avoid sharing mutable SDK sessions across worker threads.
    def worker(row):
        client=oss2.Bucket(oss2.Auth(os.environ['OSS_ACCESS_KEY_ID'],os.environ['OSS_ACCESS_KEY_SECRET']),
            'https://oss-cn-shanghai.aliyuncs.com','spend-good')
        return transfer(row,client,download)
    with ThreadPoolExecutor(max_workers=4) as pool:
        tasks={pool.submit(worker,group[0]):group for group in groups.values()}
        for task in as_completed(tasks):
            group=tasks[task]
            try:
                verified=task.result()
                for row in group:
                    result=dict(verified,**row)
                    assert result['bytes']==result['readback_bytes']
                    results.append(result)
                    print(json.dumps(dict(pid=row['pid'],url=result['oss_url'],status=200,bytes=result['readback_bytes'],sha256=result['sha256'],byte_equal=True)),flush=True)
            except Exception as error:
                for row in group:
                    skipped.append(dict(candidate=row,reason='transfer_or_readback_failed',detail=str(error)))
                    print(json.dumps(dict(pid=row['pid'],skipped=str(error))),flush=True)
            checkpoint()
    print(json.dumps(dict(verified=len(results),skipped=len(skipped))),flush=True)
if __name__=='__main__':main()
