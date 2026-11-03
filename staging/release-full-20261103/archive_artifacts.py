"""Preserve byte-exact per-family ledgers without committing thousands of loose files."""
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
P=Path(__file__).resolve().parent
DIRS=('responses','states','sent','sessions','circuit-history')
FILES=('baseline-goods.json','baseline-response.json','run.log','dispatch.json')
def main():
    paths=sorted([p for d in DIRS for p in (P/d).glob('*.json')]+[P/f for f in FILES if (P/f).exists()])
    if (P/'circuit.json').exists():paths.append(P/'circuit.json')
    manifest={str(p.relative_to(P)):dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in paths}
    with (P/'raw-artifacts.tar.gz').open('wb') as file:
        with gzip.GzipFile(fileobj=file,mode='wb',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w|') as tar:
                for p in paths:
                    info=tar.gettarinfo(str(p),arcname=str(p.relative_to(P)));info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=''
                    with p.open('rb') as handle:tar.addfile(info,handle)
    with tarfile.open(P/'raw-artifacts.tar.gz','r:gz') as tar:
        actual={m.name:dict(sha256=hashlib.sha256(tar.extractfile(m).read()).hexdigest(),bytes=m.size) for m in tar.getmembers()}
    assert actual==manifest
    out=dict(archive='raw-artifacts.tar.gz',archive_sha256=hashlib.sha256((P/'raw-artifacts.tar.gz').read_bytes()).hexdigest(),entries=len(manifest),files=manifest,roundtrip_verified=True)
    (P/'artifact-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='files'}))
if __name__=='__main__':main()
