"""Normalize exact-ID discovery quotes without relaxing reviewed price semantics."""
import math
from .price_semantics import name_kind,amount


def normalize_discovery_quote(row):
    source=row.get('name_source') or {}
    if not isinstance(source,dict):return row
    if (not str(row.get('id','')).startswith('CN:mi_cn:product:')
            or source.get('identity_verified') is not True
            or str(source.get('product_id'))!=row['id'].rsplit(':',1)[-1]):return row
    for field in ('price','market_price'):
        value=row.get(field)
        if isinstance(value,str):
            try:number=float(value)
            except ValueError:continue
            if math.isfinite(number) and number>0:row[field]=int(number) if number.is_integer() else number
    # Only repair the initial numeric-string case after a fresh numeric quote.
    # Explicit uncertainty, evidence decisions and partial-payment names stay put.
    if (row.get('price_kind')=='unknown' and isinstance(row.get('source_price'),str)
            and amount(row.get('price')) and not row.get('price_kind_evidence')
            and name_kind(row)[0] is None):
        try:old=float(row['source_price'])
        except ValueError:return row
        if math.isfinite(old) and old>0:row.pop('price_kind')
    return row
