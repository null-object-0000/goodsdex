export const hpIdentity=row=>Object.fromEntries(['source','part_number','source_url','fetched_at'].filter(k=>row[k]!=null).map(k=>[k,row[k]]));
const short=value=>String(value||'').split(/[（(，,；;]/)[0].trim();
const capacity=value=>{const m=String(value||'').match(/(\d+(?:\.\d+)?)\s*(GB|TB|G)(?![\p{L}\p{N}_])/iu);return m?m[1]+(m[2].toUpperCase()==='G'?'GB':m[2].toUpperCase()):null;};
export function canUpdateHpName(before,row){
 if(before?.id!==row?.id||before.source!=='hp_cn'||row.source!=='hp_cn'||!row.part_number||row.id!=='CN:hp_cn:sku:'+row.part_number||before.part_number!==row.part_number||before.product_id!==row.product_id||before.source_url!==row.source_url)return false;
 if(!row.source_url?.startsWith('https://www.hpstore.cn/'))return false;
 const proof=row.name_evidence,at=Date.parse(row.fetched_at),previous=Date.parse(before.fetched_at);
 if(!proof||proof.kind!=='hp_official_sku'||!/^[a-f0-9]{64}$/.test(proof.sha256||'')||proof.captured_at!==row.fetched_at||proof.source_url!==row.source_url||!Number.isFinite(at)||!Number.isFinite(previous)||at<=previous)return false;
 if(proof.context_sku!==row.part_number||proof.specification_sku!==row.part_number||proof.source_name!==row.source_name)return false;
 if(!row.product_id?.startsWith('CN:hp_cn:model:'))return false;
 try{if(decodeURIComponent(row.product_id.slice('CN:hp_cn:model:'.length))!==row.model)return false;}catch{return false;}
 const p=row.params||{};
 if(['CPU型号','运行内存','存储容量','显卡'].some(k=>typeof p[k]!=='string'||!p[k]||p[k]!==proof.specs?.[k]))return false;
 const spec=[capacity(p['运行内存']),capacity(p['存储容量'])].filter(Boolean).join('+');
 return row.name===[row.model,short(p['CPU型号']),spec,short(p['显卡'])].filter(Boolean).join(' ');
}
