"""Build supplemental patches only from byte-verified OSS transfer artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.backfill import apply
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);a=p.parse_args()
    evidence=ROOT/'docs/小米旧图入库-20261030'
    resolved={r['pid']:r for r in json.loads((evidence/'resolved.json').read_text())}
    verified=json.loads((a.artifacts/'transfer-result/oss-readback.json').read_text())
    failed=json.loads((a.artifacts/'transfer-result/skipped-transfer.json').read_text())
    skipped=json.loads((evidence/'skipped-provenance.json').read_text())+failed
    assert len({r['pid'] for r in verified})==len(verified)
    assert {r['pid'] for r in verified}|{r['candidate']['pid'] for r in failed}==set(resolved)
    patches=[]
    for r in verified:
        assert all(r.get(k)==v for k,v in resolved[r['pid']].items())
        raw=(a.artifacts/'image-transfer-cache'/Path(r['key']).name).read_bytes()
        assert r['byte_equal'] is True and r['http_status']==200
        assert len(raw)==r['readback_bytes']==r['bytes']
        assert hashlib.sha256(raw).hexdigest()==r['sha256']
        assert r['oss_url']=='https://spend-good.oss-cn-shanghai.aliyuncs.com/'+r['key']
        note='原候选 checked_at 为图片 GET 验证的观察时间，非网页采集时间或归档时间；官方来源页按已验证 specs URL 与原研究报告还原。'
        if r['image_scope']=='series':note+=' 多 pid 共用素材，仅作系列参考图，不代表某容量、配色的独占主体图。'
        fields=dict(image=r['oss_url'],image_source=r['source'],image_source_type='official',
            image_source_url=r['source_url'],image_captured_at=r['captured_at'],image_scope=r['image_scope'],image_note=note)
        patches.append(dict(id=r['id'],field='image',source=r['source'],source_url=r['source_url'],captured_at=r['captured_at'],captured_at_kind=r['captured_at_kind'],fields=fields))
    baseline=json.loads(a.baseline.read_text());result,audit=apply(baseline,patches)
    assert not audit['skipped'],audit
    assert len(audit['applied'])==len(patches)
    assert len(result)==len(baseline)
    allowed={p['id']:p['fields'] for p in patches}
    for before,after in zip(baseline,result):
        assert after==dict(before,**allowed.get(before['id'],{}))
    for name,obj in [('oss-readback.json',verified),('skipped-transfer.json',failed),('patch-audit.json',audit)]:
        (evidence/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    for name,obj in [('verified-backfill-xiaomi-images-20261030.json',patches),('backfill-skipped-xiaomi-images-20261030.json',skipped)]:
        (ROOT/'data/supplements'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print(dict(patches=len(patches),skipped=len(skipped)))
if __name__=='__main__':main()
