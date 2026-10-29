import {performance} from 'node:perf_hooks';
const {createGoodsIndex}=await import(process.argv[2]);
const at=performance.now(),index=createGoodsIndex(process.argv[3]);
await index.load();const loaded=performance.now();
const result=await index.query(new URLSearchParams({q:'',limit:'20',group_products:'1'}));
console.log(JSON.stringify({load_ms:loaded-at,first_query_ms:performance.now()-loaded,total_ms:performance.now()-at,total:result.total,facets:result.facets}));
