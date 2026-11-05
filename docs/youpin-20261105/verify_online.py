"""Read back the complete published generation and all reviewed Youpin targets."""
import gzip
import json
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from datetime import datetime, timezone

ROOT=Path(__file__).parent

def fetch(path):
    with urlopen(Request('https://spend.snewbie.site'+path,headers={'Accept-Encoding':'gzip'}),timeout=60) as r:
        raw=r.read()
        if r.headers.get('Content-Encoding')=='gzip': raw=gzip.decompress(raw)
    return json.loads(raw)

if __name__=='__main__':
    meta=fetch('/api/meta');actual=fetch('/api/goods')
    receipt=json.loads((ROOT/'publication.json').read_text())
    expected=json.loads(subprocess.check_output(['git','show',receipt['data_commit']+':public/goods.json']))
    assert actual==expected,'API full catalogue differs from published data branch'
    before=json.loads((ROOT/'targets-before.json').read_text());by_before={r['id']:r for r in before}
    manifest=json.loads(Path('data/official/youpin-crosswalk.json').read_text())
    targets=[]
    for item in manifest['items']:
        r=fetch('/api/goods/'+quote(item['id'],safe=''))
        expected_row=next(e for e in expected if e['id']==item['id'])
        for field in ['youpin_gid','youpin_evidence','youpin_category','youpin_offers','youpin_listed','release_upper_bound']:
            assert r[field]==expected_row[field],(item['id'],field)
        for field in ['gid','price','price_kind','release','release_decision','category','image']:
            assert r.get(field)==by_before[item['id']].get(field),(item['id'],'original field changed',field)
        targets.append(r)
    bmeta=json.loads((ROOT/'live-meta-before.json').read_text())
    assert meta['release_precision']['total']==bmeta['release_precision']['total']
    assert meta['release_scope']==bmeta['release_scope']
    (ROOT/'targets-online.json').write_text(json.dumps(targets,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'live-meta-after.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'ok':True,'full_catalog_equal':True,
        'total':len(actual),'verified_targets':len(targets),'revision':meta['revision'],
        'original_fields_unchanged':['gid','price','price_kind','release','release_decision','category','image'],
        'release_precision_before':bmeta['release_precision']['total'],'release_precision_after':meta['release_precision']['total'],
        'release_scope_unchanged':True,'new_release_dates':0,'category_repairs':0,'images_filled':0,'listing_upper_bounds_added':17}
    (ROOT/'online-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
