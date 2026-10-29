import hashlib
import json
import tempfile
import unittest
import base64
import gzip
from pathlib import Path
from goodsdex.shards import build_shards, shard_for

class ShardsTest(unittest.TestCase):
    def test_roundtrip_conflicts_and_determinism(self):
        rows=[dict(id='CN:mi_cn:product:1',name='测试',category='家电',categories=['家电','电饭煲'],product_id='p',record_level='sku',params={'容量':'3L','heavy':['完整参数']}),dict(id='CN:mi_cn:product:1',name='测试',category='厨房',params={'容量':'4L'}),dict(id='brand:new',name='新品',brand='新品牌',params={'a':1})]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);original=json.dumps(rows,ensure_ascii=False).encode();(root/'goods.json').write_bytes(original)
            meta=build_shards(root)
            self.assertEqual((root/'goods.json').read_bytes(),original)
            self.assertEqual(meta['count'],3);self.assertEqual(meta['unique_count'],2)
            self.assertEqual(meta['schema'],1)
            for name,d in meta['files'].items():
                raw=(root/name).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),d['sha256']);self.assertEqual(len(raw),d['bytes'])
            pack=json.loads((root/'index/other.json').read_bytes())
            self.assertTrue(all('params' not in r for r in pack['items']))
            self.assertEqual(pack['items'][0]['categories'],rows[0]['categories'])
            queries=json.loads(gzip.decompress(base64.b64decode(pack['query_gzip'])))
            self.assertEqual(queries[0]['search_text'],json.dumps(rows[0]['params'],ensure_ascii=False,separators=(',', ':')).lower())
            detail=json.loads((root/f'detail/{shard_for(rows[0]["id"]):02x}.json').read_bytes())[rows[0]['id']]
            conflicts=detail.pop('_catalog_conflicts');self.assertEqual(detail,rows[0]);self.assertEqual(conflicts,[rows[1]])
            self.assertEqual(build_shards(root)['files'],meta['files'])

if __name__=='__main__':unittest.main()
