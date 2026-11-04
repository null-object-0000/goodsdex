"""Replay a frozen official dictionary and exact reviewed series memberships offline."""
from extract import *
from copy import deepcopy
from collections import Counter,defaultdict
import random
from goodsdex.series_release import apply_series_releases,is_accessory,validate_batch,reconcile_series
from goodsdex.release_crosschecks import delta_days

BUNDLE=ROOT/'data/official/series-releases.json'
DICT=ROOT/'data/official/xiaomi-release-dictionary.json'
def load_bundle():return json.loads(gzip.decompress((OUT/'series-before.json.gz').read_bytes()))
def count(rows):
    mi=[r for r in rows if r.get('brand')=='小米']
    def assertion(r):return any(bool((r.get(k) or {}).get('date')) for k in ['release','release_series'])
    def visible(r):return any(bool((r.get(k) or {}).get('date')) and (r.get(k) or {}).get('usage')!='disabled' and (r.get(k) or {}).get('display_allowed',True) for k in ['release','release_series'])
    return dict(rows=len(mi),assertion_union=sum(map(assertion,mi)),display_allowed_union=sum(map(visible,mi)),
       product=sum(bool((r.get('release') or {}).get('date')) for r in mi),series=sum(bool((r.get('release_series') or {}).get('date')) for r in mi))

def make_dictionary(before,bundle):
    byid={r['id']:r for r in before};raw=read(OUT/'archive-entries.json')+read(OUT/'reviewed-newsroom-entries.json')
    # Product parameters already evidence a specific ID. Same-name products may
    # be reissues; this source alone never expands beyond that frozen identity.
    for e in raw:
      if e['origin']=='existing_product_official':
       e['reviewed_ids']=[r['id'] for r in before if norm(r['name'])==norm(e['product_name']) and (r.get('release')or{}).get('date')==e['date']]
    seed_ids={b['id'] for b in read(ROOT/'docs/xiaomi-series-expansion-20261104/reviewed-new-batches.json')}
    for b in bundle['batches']:
      if b['id'] not in seed_ids:continue
      r=b['series_release'];assert reconcile_series(r,b['id'])['display_allowed']
      raw.append(dict(id='mi-dict-seed-'+b['id'],product_name=b['series'],date=r['date'],granularity=r['granularity'],market=r['market'],event=r['event'],
        aliases=sorted({byid[m['id']]['name'] for m in b['members']}),match='exact',evidence=r['evidence'],origin='reviewed_32_batch_seed',
        reviewed_ids=[m['id'] for m in b['members']],seed_batch_id=b['id'],generation=b['generation'],
        crosschecks=r.get('crosschecks',[])))
    unique={}
    for e in raw:
      key=(norm(e['product_name']),e['date'],e['market'],e['event'])
      if key not in unique:unique[key]=deepcopy(e)
      else:
       old=unique[key];old['aliases']=sorted(set(old['aliases']+e['aliases']))
       old.setdefault('alternate_evidence',[]).append(e['evidence'])
    dictionary=dict(schema=1,scope='CN_reviewed_release_dictionary',matching='NFKC + casefold + whitespace removal; exact aliases only. No fuzzy match, pack or capacity inheritance.',
      raw_reviewed_entries=len(raw),entries=list(unique.values()),seed_batches_crosschecked=len(seed_ids))
    write(DICT,dictionary)
    return dictionary

def main():
    before=read_baseline();original=load_bundle();bundle=deepcopy(original);dictionary=make_dictionary(before,original)
    es=dictionary['entries'];byid=defaultdict(list);names=defaultdict(set)
    for r in before:
      if r.get('brand')=='小米':byid[r['id']].append(r);names[norm(r['name'])].add(r['id'])
    def matching(r,archive_only=False):
      found=[]
      for e in es:
       if e['market']!='CN' or e['event']!='announcement':continue
       if archive_only and e['origin']=='reviewed_32_batch_seed':continue
       if e.get('reviewed_ids') and r['id'] not in e['reviewed_ids']:continue
       if norm(r['name']) not in {norm(n) for n in [e['product_name'],*e['aliases']]}:continue
       if len(names[norm(r['name'])])>1 and not e.get('reviewed_ids'):continue
       found.append(e)
      # Precision wins only among compatible claims. Do not conceal discrepancies.
      if any(a['date'][:7]!=b['date'][:7] for a in found for b in found):return []
      return sorted(found,key=lambda e:(-len(e['date']),e['origin']!='official_newsroom',e['id']))
    oldids={m['id'] for b in original['batches'][:81] for m in b['members']}
    allids={m['id'] for b in original['batches'] for m in b['members']}
    secondary={x['batch_id']:x for x in read(OUT/'reviewed-secondary.json')
               if x['batch_id']!='mi-reviewed-1006044'} # Primary proves availability, not announcement.
    membership_audit=[];repairs=[];new=[]
    for b in list(bundle['batches']):
      if b['id'] not in {x['id'] for x in original['batches'][:81]}:continue
      r=b['series_release']
      if b['id'] in secondary:
       sec=secondary[b['id']];e=sec['evidence'];r['evidence']['publisher']='ithome'
       check=dict(source='third_party',date=sec['date'],batch_id=b['id'],market='CN',event=r['event'],independent=True,
         independence_reason='原始供稿机构IT之家与快科技独立；逐条核对快科技原创署名，无IT之家转载标记。'+sec['reason'],evidence=e)
       r.setdefault('crosschecks',[]).append(check)
       assert reconcile_series(r,b['id'])['display_allowed'],b['id']
       repairs.append(dict(original_batch_id=b['id'],batch_id=b['id'],ids=[m['id'] for m in b['members']],method='independent_media_archive',evidence=e))
       continue
      # A source proving only a subset must never unlock the unproved members.
      keep=[]
      for m in b['members']:
       row=byid[m['id']][0];matches=matching(row,archive_only=True)
       if not matches or r['event']!='announcement' or delta_days(r['date'],matches[0]['date'])>14:
        keep.append(m);continue
       entry=matches[0];bid=b['id']+'-dict-'+entry['id'].split('-')[-1]
       rb=deepcopy(b);rb.update(id=bid,derived_from_batch_id=b['id'],dictionary_entry_id=entry['id'],members=[m])
       rr=rb['series_release'];rr['evidence']['publisher']='ithome'
       rr.setdefault('crosschecks',[]).append(dict(source='official',date=entry['date'],batch_id=bid,market='CN',event=rr['event'],independent=True,
         independence_reason='原始IT之家新闻稿与小米官方发布正文为不同发布机构；精确产品名/显式译名、市场、事件及同月批次均已审核。',evidence=entry['evidence']))
       assert reconcile_series(rr,bid)['display_allowed'];new.append(rb)
       repairs.append(dict(original_batch_id=b['id'],batch_id=bid,ids=[m['id']],method='official_dictionary',dictionary_entry_id=entry['id'],evidence=entry['evidence']))
      if keep:b['members']=keep
      else:bundle['batches'].remove(b)
    for id,rows in sorted(byid.items()):
      row=rows[0]
      if id in allids or any((r.get('release')or{}).get('date') for r in rows) or is_accessory(row) or row.get('kind')=='service':continue
      matches=matching(row)
      if not matches:continue
      entry=matches[0]
      if entry['evidence']['source_type']!='official':continue
      # Multiple current identity projections require explicit manual review.
      hashes={digest(identity(r)) for r in rows}
      if len(hashes)!=1:continue
      bid='mi-dictionary-'+entry['id'].split('-')[-1]+'-'+id.split(':')[-1]
      batch=dict(id=bid,series=entry['product_name'],generation='原文明确的中国大陆首发批次；只纳入精确名称审核成员',dictionary_entry_id=entry['id'],
        series_release=dict(date=entry['date'],granularity=entry['granularity'],source='official',market='CN',event=entry['event'],level='series',evidence=entry['evidence']),
        members=[dict(id=id,reviewed_name=row['name'],identity_sha256=next(iter(hashes)),identity_reason='NFKC/大小写/排版空白归一后与官方字典产品名或显式审核译名完全相同；不扩展容量、颜色、组合或型号后缀。')])
      validate_batch(batch);new.append(batch)
      membership_audit.extend(dict(id=id,name=r['name'],dictionary_entry_id=entry['id'],batch_id=bid,date=entry['date'],evidence=entry['evidence']) for r in rows)
    bundle['batches'].extend(new)
    for b in bundle['batches']:validate_batch(b)
    write(BUNDLE,bundle)
    after=apply_series_releases(before)
    assert apply_series_releases(after)==after
    unmanaged=lambda rs:[{k:v for k,v in r.items() if k!='release_series'} for r in rs]
    assert unmanaged(before)==unmanaged(after)
    assert len(before)==len(after)
    (OUT/'expected.json.gz').write_bytes(gzip.compress(json.dumps(after,ensure_ascii=False).encode(),mtime=0))
    write(OUT/'new-memberships.json',membership_audit);write(OUT/'legacy-repairs.json',repairs)
    changes=[b for b in bundle['batches'] if b not in original['batches']]
    write(OUT/'reviewed-batch-changes.json',dict(added_or_updated=changes,removed_batch_ids=[b['id'] for b in original['batches'] if b['id'] not in {b['id'] for b in bundle['batches']}]))
    repairedids={id for repair in repairs for id in repair['ids']}
    legacy=[]
    afterbyid={r['id']:r for r in after}
    for b in original['batches'][:81]:
      for m in b['members']:
       r=afterbyid[m['id']];d=r['release_series'];repaired=d['display_allowed']
       assert d['date']==b['series_release']['date'] and d['evidence']['url']==b['series_release']['evidence']['url']
       legacy.append(dict(id=r['id'],name=r['name'],original_batch_id=b['id'],batch_id=d['batch_id'],repaired=repaired,
         reason='独立第二来源已核对同批次/市场/事件' if repaired else '本轮官方归档/日期聚合新闻未取得同代际、同市场、同事件的第二独立原句；同名近似、海外日期、后续版本或仅开售/预售片段均不能解锁',
         original_date=d['date'],crosscheck_status=d['crosscheck_status']))
    write(OUT/'legacy-149.json',legacy)
    unresolved=read(ROOT/'docs/xiaomi-series-expansion-20261104/unresolved.json');covered={a['id'] for a in membership_audit}
    remaining=[]
    for f in unresolved:
      members=[m for m in f['members'] if m['id'] not in covered]
      if not members:continue
      f=deepcopy(f);f.update(members=members,row_count=len(members),sku_count=len({m['id'] for m in members}))
      r=afterbyid[members[0]['id']]
      if is_accessory(r) or r.get('kind')=='service':reason='配件/耗材/服务不适用系列日期；不放宽原过滤规则'
      elif len(names[norm(r['name'])])>1:reason='当前同名不同ID，不能仅靠名称确定是否同一发布批次'
      elif any(norm(r['name']).startswith(norm(e['product_name'])) for e in es):reason='只有较宽系列或近似前缀；规格、后加配色/组合/容量/年份未在归档中明确同批推出'
      else:reason='本轮已抓取的官方发展历程、249篇新闻索引及145篇相关正文/既有业绩公告中，没有可精确匹配的大陆发布条目；不是宣称全网不存在'
      f.update(reason=reason,status='unmatched_official_dictionary');remaining.append(f)
    remaining.sort(key=lambda f:(-f['row_count'],f['family']))
    write(OUT/'unmatched.json',remaining);write(OUT/'unmatched-top20.json',remaining[:20])
    # Seven new matches exist. Audit changed memberships including second-source repairs.
    rng=random.Random(20261104)
    changed_pool=membership_audit+[dict(id=id,name=byid[id][0]['name'],batch_id=repair['batch_id'],
       dictionary_entry_id=repair.get('dictionary_entry_id'),method=repair['method'],evidence=repair['evidence'])
       for repair in repairs for id in repair['ids']]
    assert len(changed_pool)>=30
    anchored=[]
    for item in changed_pool[len(membership_audit):]:
      row=byid[item['id']][0]
      release=next(b['series_release'] for b in bundle['batches'] if b['id']==item['batch_id'])
      candidates=[e for e in es if e['event']==release['event'] and e['date'][:7]==release['date'][:7]
        and norm(row['name']) in {norm(n) for n in [e['product_name'],*e['aliases']]}
        and (not e.get('reviewed_ids') or row['id'] in e['reviewed_ids'])]
      if not candidates:continue
      item=deepcopy(item);item['dictionary_entry_id']=item.get('dictionary_entry_id') or candidates[0]['id'];anchored.append(item)
    assert len(anchored)>=30-len(membership_audit)
    samples=membership_audit+rng.sample(anchored,30-len(membership_audit))
    write(OUT/'sample-30.json',samples)
    fetches=[json.loads(l) for l in (OUT/'fetches.jsonl').read_text().splitlines()]
    starts=sorted(c['started_epoch'] for c in fetches)
    assert all(b-a>=2.099 for a,b in zip(starts,starts[1:])), 'request spacing'
    beforecounts=count(before);aftercounts=count(after)
    report=dict(before=beforecounts,after=aftercounts,baseline_full_rows=len(before),
      baseline_unresolved_families=1385,baseline_unresolved_rows=1417,new_matched_rows=len(membership_audit),new_unique_ids=len(covered),
      matched_unresolved_families=sum(any(m['id'] in covered for m in f['members']) for f in unresolved),
      remaining_unresolved_families=len(remaining),remaining_unresolved_rows=sum(f['row_count'] for f in remaining),
      legacy_repaired=sum(x['repaired'] for x in legacy),legacy_still_disabled=sum(not x['repaired'] for x in legacy),
      dictionary_raw_reviewed_entries=dictionary['raw_reviewed_entries'],dictionary_dedup_entries=len(es),dictionary_official_entries=sum(e['evidence']['source_type']=='official' for e in es),
      fetch_requests=len(fetches),successful_responses=sum(c.get('status')==200 for c in fetches),
      failed_or_redirects=sum(c.get('status')!=200 for c in fetches),newsroom_index_items=len(read(OUT/'newsroom-index.json')),newsroom_body_items=len(read(OUT/'articles.json')),
      minimum_request_spacing_seconds=min(b-a for a,b in zip(starts,starts[1:])),
      goals_met=dict(dictionary_300=len(es)>=300,new_rows_400=len(membership_audit)>=400,display_25pct=aftercounts['display_allowed_union']/aftercounts['rows']>=.25),
      invariants=dict(non_series_fields_unchanged=True,product_dates_unchanged=True,other_brands_unchanged=True,row_count_unchanged=True,idempotent=True,gate_code_unchanged=True,no_fuzzy_matching=True),
      sample=dict(seed=20261104,pool='all_new_matches_plus_sampled_legacy_repairs',pool_size=len(changed_pool),size=30))
    write(OUT/'report.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
