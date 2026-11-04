"""Validate a complete anonymous H5 snapshot and merge SKU rows; never finalize."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.atour import merge_snapshot
from goodsdex.archive import merge_archive
from goodsdex.price_history import observation, stage

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--capture',type=Path,required=True);ap.add_argument('--public',type=Path,required=True)
    a=ap.parse_args();capture=json.loads(a.capture.read_text());previous=json.loads((a.public/'goods.json').read_text())
    rows=merge_snapshot(previous,capture)
    current=[r for r in rows if r.get('source')=='atour' and r.get('status')!='retired']
    records=[dict(product=dict(variant_id=r['id'],name=r['name'],kind=r['kind']),view=dict(values=dict(price=r['price'],specs=r['specs'],sku_no=r['sku_no']))) for r in current]
    merge_archive('atour',records,archive_dir=a.public/'archive',now_iso=capture['captured_at'],discovery=dict(completeness='complete',total_reported=len(current),found=len(current),stop_reason='reached_total'))
    target=a.public/'goods.json';tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(rows,ensure_ascii=False,indent=1)+'\n');tmp.replace(target)
    old_retired={r['id'] for r in previous if r.get('status')=='retired'}
    events=[observation(r,status='unavailable' if r.get('official_sku_status') != 1 else None) for r in current]
    events += [observation(r,at=capture['captured_at'],status='unavailable') for r in rows if r.get('source')=='atour' and r.get('status')=='retired' and r['id'] not in old_retired]
    stage(a.public,events)
    print(f'Atour complete: {len({r["spu_id"] for r in current})} SPU / {len(current)} SKU')
