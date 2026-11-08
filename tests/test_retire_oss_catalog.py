import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from retire_oss_catalog import is_catalogue


def test_private_backup_scope_never_includes_images_or_original_evidence():
    for key in ['data/public/goods.json','data/public/index/mi_cn.json','data/public/blobs/abc/goods.json','data/public/prices/2026-11.jsonl.gz']:
        assert is_catalogue(key)
    for key in ['goods/photo.jpg','data/public/blobs/abc/photo.jpg','data/public/archive/evidence.html','data/public/evidence/report.json','other/goods.json']:
        assert not is_catalogue(key)
