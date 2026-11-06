"""Audit product-source migration, or snapshot/restore a complete public release."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tarfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.product_sources import apply_sources, coverage


def snapshot(public, backup):
    public, backup = Path(public), Path(backup)
    if backup.exists():
        raise ValueError('Backup already exists; refusing to overwrite')
    with tarfile.open(backup, 'w:gz') as archive:
        archive.add(public, arcname='public', recursive=True)


def restore(public, backup):
    public = Path(public)
    # Validate all entries before writing. No links or paths outside public.
    with tarfile.open(backup, 'r:gz') as archive:
        for member in archive.getmembers():
            p = Path(member.name)
            if not p.parts or p.parts[0] != 'public' or '..' in p.parts or not (member.isfile() or member.isdir()):
                raise ValueError('Unsafe backup entry')
        expected = set()
        for member in archive.getmembers():
            relative = Path(*Path(member.name).parts[1:])
            target = public / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
                expected.add(relative)
    # Remove only generated files introduced since the snapshot.
    for path in public.rglob('*'):
        if path.is_file() and path.relative_to(public) not in expected:
            path.unlink()


def audit(input_path, output):
    raw = Path(input_path).read_bytes()
    rows = json.loads(gzip.decompress(raw) if str(input_path).endswith('.gz') else raw)
    migrated = apply_sources(rows, rows)
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    def write(name, value):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    report = coverage(migrated)
    report['input_sha256'] = hashlib.sha256(raw).hexdigest()
    report['removed_legacy_fields'] = [dict(id=a['id'], removed=sorted(a.keys()-b.keys())) for a,b in zip(rows,migrated) if a.keys()-b.keys()]
    report['value_changes'] = [dict(id=a['id'], fields={k:dict(before=a.get(k),after=b.get(k)) for k in ('name','image','category','price') if a.get(k)!=b.get(k)}) for a,b in zip(rows,migrated) if any(a.get(k)!=b.get(k) for k in ('name','image','category','price'))]
    report['priceless_before'] = sum(r.get('price') is None for r in rows)
    report['priceless_after'] = sum(r.get('price') is None for r in migrated)
    samples=[]
    for predicate in (lambda r:r.get('discovered_by')=='mihome_directory' and r.get('source')=='mihome',
                      lambda r:r['primary_source']=='mi_store' and len(r['sources'])>1,
                      lambda r:r['primary_source']=='apple_store',lambda r:r['primary_source']=='hp_support',
                      lambda r:r['primary_source']=='atour_official'):
        r=next(r for r in migrated if predicate(r))
        samples.append({k:r[k] for k in ('id','primary_source','sources','display','source_history','price_missing') if k in r})
    write('samples.json',samples); write('statistics.json',report)
    (output/'goods.json.gz').write_bytes(gzip.compress(json.dumps(migrated,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    print(json.dumps({k:v for k,v in report.items() if k!='value_changes'},ensure_ascii=False,indent=2))
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('audit');a.add_argument('--input',required=True);a.add_argument('--output',required=True)
    for name in ('snapshot','restore'):
        a=sub.add_parser(name);a.add_argument('--public',required=True);a.add_argument('--backup',required=True)
    args=p.parse_args()
    if args.command=='audit':audit(args.input,args.output)
    elif args.command=='snapshot':snapshot(args.public,args.backup)
    else:restore(args.public,args.backup)
