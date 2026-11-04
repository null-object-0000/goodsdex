"""Replay the manually reviewed four exact-ID assertions; discovery cannot publish.

Run from repository root:
  PYTHONPATH=src python3 docs/release-dates-round6-20261104/build_reviewed.py BASELINE.json [--apply]
The baseline is public/goods.json from the pinned data revision, not main's stale public/.
"""
import argparse, gzip, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from goodsdex.release_dates import apply_release_dates, validate
ROOT=Path(__file__).resolve().parent
INPUT=Path('data/official/release-dates.json')

def load_capture(path):
 o=json.loads(Path(path).read_text());raw=gzip.decompress((Path(path).parent/o['raw_file']).read_bytes()) if '/' not in o['raw_file'] else gzip.decompress(Path(o['raw_file']).read_bytes())
 assert hashlib.sha256(raw).hexdigest()==o['sha256'],path
 assert o['http_status']==200,path
 return o

def build(rows):
 by={r['id']:r for r in rows};new=[]
 def add(key,date,event,path,quote,more,identity):
  row=by[key];assert not (row.get('release') or {}).get('date'),key
  assert row.get('kind')!='accessory',key
  o=load_capture(path)
  for q in [quote]+more:assert q in o['text'],(key,q)
  ev=dict(url=o['url'],quote=quote,supporting_quotes=more,locator=identity,source_type='official',sha256=o['sha256'],captured_at=o['captured_at'])
  c=dict(family='round6:'+key,ids=[key],name=row['name'],brand=row['brand'],method='explicit_dated_statement',capture_file=str(Path(path).relative_to(Path.cwd()) if Path(path).is_absolute() else path),identity_review=identity,release=dict(date=date,event=event,source='official',confidence='high',granularity='month',market='CN',evidence=ev))
  validate(c);new.append(c)
 def captured(url):
  return next(p for p in (ROOT/'evidence').glob('*.json') if json.loads(p.read_text())['url']==url)
 add('CN:dji:sku:107481','2021-10','announcement','docs/release-dates-round4-20261103/evidence/681816a21b23fa51ed04.json',
     '（ 2021 年 10 月 20 日 深圳 ）今日， DJI 大疆创新通过全球直播的方式推出全新电影摄影机 DJI Ronin 4D 。',
     ['DJI Ronin 4D 分为 6K 和 8K 两个版本， 6K 套装售价 46888 元，含机身、禅思 X9-6K 云台相机、 LiDAR 测距器、机身高亮监视器、控制手柄及提手、 TB 50 智能电池以及其他相关配件。','6K 版本将于 12 月在 DJI 官方商城和相关渠道发售， 8K 版本也将在随后发售，详细信息请留意后续官方信息。'],
     '正文日期及发售与售后信息；仅匹配6K型号，不采用12月计划开售或8K基础版')
 add('CN:dji:sku:121851','2022-09','availability','docs/release-dates-round4-20261103/evidence/073c14d1dbc5b032e03f.json',
     'Osmo Mobile 6 售价 999 元，包含手机云台以及磁吸手机夹、手持三脚架、束口袋、充电线等配件，即日起， DJI 大疆官方商城、京东、天猫、北京旗舰店、上海旗舰店、南京旗舰店、杭州旗舰店以及全国线下授权体验店等渠道现货发售。',
     ['（ 2022 年 9 月 22 日 深圳） DJI 大疆今日正式发布新一代智能防抖手机云台 Osmo Mobile 6 ，','Osmo Mobile 6 外观全新升级，暗岩灰配色凸显高级。'],
     '正文日期、暗岩灰配色及售价与服务；浅银灰SKU排除')
 add('CN:dji:sku:275601','2026-09','availability',captured('https://store.dji.com/cn/product/dji-power-auro-2000-elite?vid=275601'),
     '“DJI 首创”指于 2026 年 9 月上市的 DJI Power Auro 2000 Elite 是 DJI 首款内置 600 瓦行车闪充及 MPPT 模块的户外电源产品。',[],
     '单品页脚注8明确点名本型号上市月份；六个加配套装不采')
 add('CN:byd:car:goods-151:2026:dmi','2025-11','announcement',captured('https://www.byd.com/cn/live-list/livedetail138'),
     '满载全家人的爱—2026款夏上市发布会 发布于 2025-11-04 19:00:00',[],
     '2026款夏上市发布会标题及直播日期；官方直播列表liveDate交叉核对2025-11-04，不以年款推算日期')
 return new

def stats(rows):
 out={}
 for b in ['惠普','比亚迪','大疆','Apple','富士']:
  rs=[r for r in rows if r.get('brand')==b]
  direct=sum((r.get('release') or {}).get('source') in ('official','third_party') and bool((r.get('release') or {}).get('date')) for r in rs)
  legacy=sum(bool((r.get('release') or {}).get('date')) for r in rs)
  shown=sum(any((r.get(f) or {}).get('date') for f in ['release','release_llm']) for r in rs)
  out[b]=dict(total=len(rs),direct_release=direct,release_including_legacy_llm=legacy,release_or_release_llm=shown,direct_coverage=direct/len(rs),combined_coverage=shown/len(rs))
 return out

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('baseline',type=Path);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 rows=json.loads(a.baseline.read_text());new=build(rows);bundle=json.loads(INPUT.read_text());bundle['candidates']=[c for c in bundle['candidates'] if not c['family'].startswith('round6:')]+new
 for c in bundle['candidates']:validate(c)
 tmp=ROOT/'reviewed-input.tmp.json';tmp.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
 try:
  after=apply_release_dates(rows,path=tmp,llm_path='data/llm/release-dates.json',crosscheck_path='data/llm/release-crosschecks.json')
  assert apply_release_dates(after,path=tmp,llm_path='data/llm/release-dates.json',crosscheck_path='data/llm/release-crosschecks.json')==after
 finally:tmp.unlink()
 old_by={r['id']:r for r in rows};new_ids={c['ids'][0] for c in new}
 for old,row in zip(rows,after,strict=True):
  assert old['id']==row['id']
  assert {k:v for k,v in row.items() if k!='release'}=={k:v for k,v in old.items() if k!='release'}
  if (old.get('release') or {}).get('date'):assert old['release']==row['release']
 actual={r['id'] for r in after if (r.get('release') or {}).get('date') and not (old_by[r['id']].get('release') or {}).get('date')};assert actual==new_ids
 report=dict(baseline_sha256=hashlib.sha256(a.baseline.read_bytes()).hexdigest(),before=stats(rows),after=stats(after),new_ids=sorted(actual),invariants=dict(non_release_fields_equal=True,old_release_objects_equal=True,new_rows=len(actual),replay_idempotent=True))
 for name,obj in [('new-candidates.json',new),('coverage.json',report)]: (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 Path('/tmp/goodsdex-round6-after.json').write_text(json.dumps(after,ensure_ascii=False))
 if a.apply:INPUT.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
