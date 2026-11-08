import {readFile} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createInterface} from 'node:readline';
import {createHash} from 'node:crypto';
import {gzipSync,createGunzip} from 'node:zlib';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

export function canonical(v){return Array.isArray(v)?v.map(canonical):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v;}
export const hash=v=>createHash('sha256').update(JSON.stringify(canonical(v))).digest('hex');
const normalized=v=>String(v??'').normalize('NFKC').replace(/\s+/g,'').toLowerCase();

export function plan(rows,baseline) {
  const known=new Map(baseline.rows.map(r=>[r.id,r])),ids=new Set(),changed=[];
  for(const row of rows){
    if(!row.id||ids.has(row.id))throw Error('Duplicate or missing source identity: '+row.id);
    ids.add(row.id);
    const old=known.get(row.id);
    if(old?.sha256===hash(row))continue;
    for(const key of ['name','gid','product_id'])if(old?.identity?.[key]!=null&&normalized(old.identity[key])!==normalized(row[key]))throw Error(`Source identity changed: ${row.id} (${key}); evidence review required, no batches uploaded`);
    changed.push(row);
  }
  // Missing source IDs are retained in MySQL. Publication never hard-deletes products.
  return changed;
}

async function readVerified(root,meta,name){
  const bytes=await readFile(path.join(root,name)),descriptor=meta.files[name];
  if(!descriptor||createHash('sha256').update(bytes).digest('hex')!==descriptor.sha256||bytes.length!==descriptor.bytes)throw Error('Invalid published artifact: '+name);
  return JSON.parse(bytes);
}

export async function publishHistory({root,meta,baseline,request,dryRun}) {
  const descriptors=meta.price_history?.files||{},known=new Set(baseline.historyFiles||[]);
  const canonicalNames=Object.keys(descriptors).filter(n=>/^price-history\/\d{4}-\d{2}(?:-[ab])?\.jsonl\.gz$/.test(n));
  const names=canonicalNames.length?canonicalNames:Object.keys(descriptors).filter(n=>/^prices\/\d{4}-\d{2}\.jsonl$/.test(n));
  let chunks=0,wireBytes=0;
  for(const name of names.sort()) {
    const descriptor=descriptors[name];if(known.has(descriptor.sha256))continue;
    const filename=path.join(root,name),digest=createHash('sha256');let bytes=0;
    for await(const part of createReadStream(filename)){digest.update(part);bytes+=part.length;}
    if(bytes!==descriptor.bytes||digest.digest('hex')!==descriptor.sha256)throw Error('Invalid history artifact: '+name);
    const input=createReadStream(filename),lines=createInterface({input:name.endsWith('.gz')?input.pipe(createGunzip()):input,crlfDelay:Infinity});
    let batch=[],size=0;
    async function flush(){
      if(!batch.length)return;const jsonl=batch.join('\n')+'\n',sha256=createHash('sha256').update(jsonl).digest('hex');
      if(!known.has(sha256)){chunks++;const body={month:name.match(/\d{4}-\d{2}/)[0],sha256,jsonl};if(!dryRun){await request('history',body);wireBytes+=gzipSync(JSON.stringify(body)).length;}}
      known.add(sha256);batch=[];size=0;
    }
    for await(const line of lines){
      if(!line.trim())continue;
      const row=JSON.parse(line),at=row.at||row.fetched_at;
      if(baseline.historyCutoff&&Date.parse(at)<Date.parse(baseline.historyCutoff))continue;
      const length=Buffer.byteLength(line)+1;if(length>8*1024*1024)throw Error('Oversized history observation');
      if(batch.length>=2000||size+length>8*1024*1024)await flush();batch.push(line);size+=length;
    }
    await flush();
  }
  return {chunks,wireBytes};
}

export async function publish({root,baseUrl,token,fetchImpl=fetch,dryRun=false}){
  const endpoint=new URL(baseUrl);
  if(endpoint.protocol!=='https:'||endpoint.username||endpoint.password)throw Error('An HTTPS catalogue API URL is required');
  if(!token||token.length<32)throw Error('Dedicated catalogue import token is required');
  const request=async(name,body)=>{
    const wire=body?gzipSync(JSON.stringify(body)):null;
    for(let attempt=0;attempt<3;attempt++){
      const response=await fetchImpl(new URL('/admin/api/catalog/'+name,endpoint),{method:wire?'POST':'GET',headers:{authorization:'Bearer '+token,...(wire?{'content-type':'application/json','content-encoding':'gzip'}:{})},body:wire,signal:AbortSignal.timeout(120000),redirect:'error'}).catch(error=>{if(attempt===2)throw Error('Catalogue API network failure');return null;});
      if(!response)continue;
      if(!response.ok){if(response.status>=500&&attempt<2)continue;throw Error(`Catalogue API rejected ${name}: HTTP ${response.status}`);}
      return response.json();
    }
  };
  const baseline=await request('baseline'),meta=JSON.parse(await readFile(path.join(root,'meta.json'),'utf8'));
  const rows=[];
  for(const name of Object.keys(meta.files).filter(n=>/^detail\/[a-f0-9]{2}\.json$/.test(n)).sort())rows.push(...Object.values(await readVerified(root,meta,name)));
  if(!rows.length)throw Error('Verified detail shards are required');
  if(meta.files['goods-excluded.json'])rows.push(...(await readVerified(root,meta,'goods-excluded.json')).items);
  const changed=plan(rows,baseline);
  let version=baseline.version,wireBytes=0,batches=0;
  if(!dryRun)for(let start=0;start<changed.length;){
    let batchRows=changed.slice(start,start+50),data,batch;
    for(;;){data={base_version:version,source_id:'goodsdex',rows:batchRows};batch={...data,batch_id:hash(data)};const plain=Buffer.byteLength(JSON.stringify(batch)),size=gzipSync(JSON.stringify(batch)).length;if(plain<=31*1024*1024&&size<=7*1024*1024){wireBytes+=size;break;}if(batchRows.length===1)throw Error('Single source record exceeds bounded importer capacity');batchRows=batchRows.slice(0,Math.ceil(batchRows.length/2));}
    const result=await request('import',batch);version=result.version;batches++;start+=batchRows.length;
  }
  const history=await publishHistory({root,meta,baseline,request,dryRun});
  return {total:rows.length,changed:changed.length,batches,wireBytes,version,dryRun,history};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  try{console.log(JSON.stringify(await publish({root:process.argv[2]||'_data/public',baseUrl:process.env.CATALOG_API_URL,token:process.env.CATALOG_IMPORT_TOKEN,dryRun:process.argv.includes('--dry-run')})));}
  catch(error){console.error(error.message);process.exitCode=1;}
}
