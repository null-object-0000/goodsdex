import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from dji_http import Client
from dji_inventory import inventory

class HTTPDisciplineTests(unittest.TestCase):
    def test_previous_attempts_exhaust_budget_across_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'requests.jsonl').write_text('{}\n')
            client=Client(root,limit=1)
            with patch('subprocess.run') as request:
                with self.assertRaisesRegex(RuntimeError,'budget'):client.fetch('https://store.dji.com/cn')
                request.assert_not_called()
            client.lock.close()

    def test_cached_capture_replays_without_requests(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client=Client(root,offline=True)
            url='https://store.dji.com/cn';key=hashlib.sha256(url.encode()).hexdigest()
            (client.cache/(key+'.body')).write_text('real captured body')
            (client.cache/(key+'.json')).write_text(json.dumps({'url':url,'status':200}))
            with patch('subprocess.run') as request:
                self.assertEqual(client.fetch(url)[0],'real captured body');request.assert_not_called()
            self.assertEqual(client.network,0);client.lock.close()

    def test_account_and_cart_paths_are_never_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client(Path(tmp))
            with patch('subprocess.run') as request:
                for path in ['/api/v5/cart','/api/client/variants','/cn/cart','/cn/checkout']:
                    self.assertEqual(client.fetch('https://store.dji.com'+path)[1]['reason'],'url_policy')
                request.assert_not_called()
            client.lock.close()

    def test_paginated_inventory_checks_total_and_reuses_finished_capture(self):
        class Fake:
            def __init__(self,root):self.root=root;self.pages=[]
            def log(self,*args):pass
            def fetch(self,url):
                if url.endswith('/cn'):return '/cn/list/accessories',{'status':200}
                if url.endswith('/cn/list/accessories'):return '<script>window.__PRELOADED_STATE__={"list":{"selected":{"tab":"103"}}};</script>',{'status':200}
                from urllib.parse import parse_qs,urlsplit
                page=int(parse_qs(urlsplit(url).query)['page'][0]);self.pages.append(page)
                return json.dumps({'success':True,'data':{'page':{'current':page,'pageSize':1,'total':2},'items':[{'variantId':page,'slug':str(page)}]}}),{'status':200}
        with tempfile.TemporaryDirectory() as tmp:
            fake=Fake(Path(tmp));a=inventory(fake)
            self.assertEqual(fake.pages,[1,2]);self.assertTrue(a['complete']);self.assertEqual(len(a['items']),2)
            inventory(fake);self.assertEqual(fake.pages,[1,2])

if __name__=='__main__':unittest.main()
