import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import path from 'node:path';
const pending=new Map();
export const digest=buf=>createHash('sha256').update(buf).digest('hex');
export function validDescriptor(name,d) {
  if(!/^(?:index\/[a-z0-9_-]+|detail\/[a-f0-9]{2}|goods)\.json$/.test(name)||!d||!/^[a-f0-9]{64}$/.test(d.sha256)||!Number.isSafeInteger(d.count)||d.count<0||!Number.isSafeInteger(d.bytes)||d.bytes<1)throw Error('无效的商品文件清单');
  return d;
}
export async function downloadCatalogFile(sources,name,descriptor,fetchImpl=globalThis.fetch) {
  validDescriptor(name,descriptor);
  let error;
  for(const source of sources)try {
    const res=await fetchImpl(`${source.replace(/\/$/,'')}/blobs/${descriptor.sha256}.json`,{signal:AbortSignal.timeout(25000)});
    if(!res.ok)throw Error(`HTTP ${res.status}`);
    const buf=Buffer.from(await res.arrayBuffer());
    if(buf.length!==descriptor.bytes||digest(buf)!==descriptor.sha256)throw Error('商品文件 SHA-256 不符');
    return buf;
  }catch(e){error=e;}
  throw error||Error('没有商品数据源');
}
export async function readCatalogFile(root,name,descriptor) {
  validDescriptor(name,descriptor);
  const target=path.join(root,name);
  try {const buf=await readFile(target);if(digest(buf)===descriptor.sha256)return buf;}catch(e){if(e.code!=='ENOENT')throw e;}
  if(pending.has(target))return pending.get(target);
  const task=(async()=>{
    const sources=JSON.parse(await readFile(path.join(root,'sources.json'),'utf8'));
    const buf=await downloadCatalogFile(sources,name,descriptor);
    await mkdir(path.dirname(target),{recursive:true});await writeFile(target+'.tmp',buf);await rename(target+'.tmp',target);return buf;
  })().finally(()=>pending.delete(target));
  pending.set(target,task);return task;
}
