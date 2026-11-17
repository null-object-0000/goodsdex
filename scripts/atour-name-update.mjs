// Titles are mutable descriptions. Atour changes require a fresh, bound official
// observation of the same immutable SPU/SKU, never just a different title.
export const atourIdentity = row => Object.fromEntries(
  ['source','spu_id','sku_id','sku_no','captured_at','fetched_at'].filter(k=>row[k]!=null).map(k=>[k,row[k]]));
export function canUpdateAtourName(before, row) {
  if (before?.source !== 'atour' || row?.source !== 'atour' || before.id !== row.id) return false;
  if (!Number.isSafeInteger(row.spu_id) || row.spu_id <= 0 || !Number.isSafeInteger(row.sku_id) || row.sku_id <= 0 || typeof row.sku_no !== 'string' || !row.sku_no) return false;
  if (row.id !== `CN:atour:spu:${row.spu_id}:sku:${row.sku_no}`) return false;
  if (['spu_id','sku_id','sku_no'].some(k=>before[k] !== row[k])) return false;
  const proof = row.name_evidence;
  if (!proof || proof.kind !== 'atour_official_sku' || !/^[a-f0-9]{64}$/.test(proof.capture_sha256 || '')) return false;
  if (proof.source_url !== `https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=${row.spu_id}` || row.source_url !== proof.source_url) return false;
  const at = Date.parse(proof.captured_at), previous = Date.parse(before.captured_at || before.fetched_at);
  if (!Number.isFinite(at) || !Number.isFinite(previous) || at <= previous || proof.captured_at !== row.captured_at || row.fetched_at !== row.captured_at) return false;
  const {listing, detail, sku} = proof;
  if (listing?.id !== row.spu_id || detail?.id !== row.spu_id || sku?.spuId !== row.spu_id || sku?.id !== row.sku_id || sku?.skuNo !== row.sku_no) return false;
  if (typeof listing.spuName !== 'string' || !listing.spuName.startsWith('亚朵星球 ') || listing.spuName !== detail.spuName || listing.spuName !== row.official_name) return false;
  if (typeof sku.skuName !== 'string' || !sku.skuName.trim() || sku.skuName !== row.sku_name) return false;
  return row.name === listing.spuName + ' / ' + sku.skuName;
}
