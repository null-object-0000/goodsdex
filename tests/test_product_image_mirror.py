import importlib.util
from pathlib import Path
from datetime import datetime,timezone,timedelta
import io
import pytest
from PIL import Image

spec=importlib.util.spec_from_file_location('product_image_mirror',Path(__file__).parents[1]/'scripts/mirror_product_images.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
SRC='https://cdn.cnbj1.fds.api.mi-img.com/example.png'

def test_existing_resized_covers_and_recent_failures_do_not_download_again():
    now=datetime.now(timezone.utc)
    assert m.pending([SRC+'?thumb=1&w=320&h=320'],{m.keys(SRC)[0]:{'objectKey':'goods/a.webp'}},now)==[]
    route={m.keys(SRC)[0]:{'objectKey':None,'checkedAt':now.isoformat()}}
    assert m.pending([SRC],route,now)==[]
    assert m.pending([SRC],route,now+timedelta(days=1))==[SRC]

def test_compressed_webp_retains_transparency_and_limits_dimensions():
    source=io.BytesIO();Image.new('RGBA',(1600,900),(255,0,0,0)).save(source,format='PNG')
    result=m.convert(source.getvalue())
    with Image.open(io.BytesIO(result)) as image:
        assert image.format=='WEBP' and max(image.size)==480
        assert image.getpixel((0,0))[3]==0

def test_sources_and_redirects_cannot_reach_arbitrary_hosts():
    with pytest.raises(ValueError):m.download('https://127.0.0.1/private')
    with pytest.raises(ValueError):m.download('https://cdn.cnbj1.fds.api.mi-img.com@127.0.0.1/a')
    class Response:
        status_code=302;headers={'Location':'http://169.254.169.254/'}
        def close(self):pass
    with pytest.raises(ValueError):m.download(SRC,get=lambda *a,**k:Response())

def test_source_failures_are_cached_but_oss_permission_failures_abort(monkeypatch):
    monkeypatch.setattr(m,'download',lambda src:(_ for _ in ()).throw(ValueError('404')))
    assert m.mirror(SRC,None)==({'sourceUrl':SRC,'objectKey':None},0)
    monkeypatch.setattr(m,'download',lambda src:b'raw')
    monkeypatch.setattr(m,'convert',lambda raw:b'webp')
    class Bucket:
        def put_object(self,*a,**k):raise PermissionError('AccessDenied')
    with pytest.raises(PermissionError):m.mirror(SRC,Bucket())
