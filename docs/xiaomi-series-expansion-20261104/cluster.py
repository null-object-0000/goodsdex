"""Research census only. No date inheritance is performed by this clustering."""
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import unicodedata

OUT = Path(__file__).parent

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def canonical(row):
    # Keep every generation, capacity, screen size, suffix, edition and colour.
    # Only typography is normalised. Reviewed co-launch batches are joined later.
    name = unicodedata.normalize('NFKC', row['name']).upper()
    return re.sub(r'\s+', '', name)

def main():
    raw = gzip.decompress((OUT / 'baseline.json.gz').read_bytes())
    rows = json.loads(raw)
    missing = [r for r in rows if r.get('brand') == '小米'
               and not (r.get('release') or {}).get('date')
               and not (r.get('release_series') or {}).get('date')]
    groups = defaultdict(list)
    for index, row in enumerate(missing):
        groups[canonical(row)].append(dict(row_index=index, id=row['id'], name=row['name'],
                                           params=row.get('params'), category=row.get('category')))
    families = []
    for key, members in groups.items():
        names = list(dict.fromkeys(r['name'] for r in members))
        years = re.findall(r'20\d{2}', names[0])
        families.append(dict(family_id='mi-research-' + hashlib.sha256(key.encode()).hexdigest()[:12],
            family=names[0], generation=('型号标注' + '/'.join(years) if years else '代际待证据核定'),
            sku_count=len({r['id'] for r in members}), row_count=len(members),
            coverage=0, method='待核；名称只作检索键，不赋日期', members=members))
    write('families-before.json', families)
    write('census-baseline.json', dict(total_rows=len(rows), xiaomi_rows=1684, missing_rows=len(missing),
          research_groups=len(families), baseline_sha256=hashlib.sha256(raw).hexdigest(),
          note='研究分组并非已经证实同代同批；未以品类、相似名称或年份代替批次证据'))
    print(len(missing), 'rows;', len(families), 'conservative research groups')

if __name__ == '__main__':
    main()
