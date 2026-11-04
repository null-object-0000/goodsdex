"""Lossless official Xiaomi page names; model/grouping names never replace them."""
from copy import deepcopy
from html.parser import HTMLParser
from datetime import datetime
import json
import html
from pathlib import Path

SUFFIX = '立即购买-小米商城'
DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/mi-page-names.json'


def page_name(document):
    class Title(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.inside = False
            self.parts = []
        def handle_starttag(self, tag, attrs):
            if tag == 'title': self.inside = True
        def handle_endtag(self, tag):
            if tag == 'title': self.inside = False
        def handle_data(self, text):
            if self.inside: self.parts.append(text)
    parser = Title()
    parser.feed(document)
    title = ''.join(parser.parts).strip()
    if not title.endswith(SUFFIX):
        raise ValueError('Not a Xiaomi purchase page title')
    name = title[:-len(SUFFIX)].strip()
    if not name:
        raise ValueError('Empty official product name')
    return name


def apply_page_names(rows, manifest=None):
    """Replay evidence only onto observed IDs; fresh page captures take priority.

    No price, identity, image or other facts are copied across products. The
    previous name remains in provenance when a cached collector is corrected.
    """
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text()) if DEFAULT.exists() else {'schema': 1, 'items': []}
    if manifest['schema'] != 1:
        raise ValueError('Unsupported Xiaomi name evidence')
    from goodsdex.source_urls import mi_url
    approved = {}
    for entry in manifest['items']:
        key = entry['id']
        if (key in approved or not mi_url(key) or entry['status'] != 200
                or entry['url'] != mi_url(key) or entry['final_url'] != entry['url']
                or page_name('<title>' + html.escape(entry['title']) + '</title>') != entry['name']
                or len(entry['sha256']) != 64):
            raise ValueError('Invalid official name evidence: ' + key)
        approved[key] = entry
    result = deepcopy(rows)
    for row in result:
        entry = approved.get(row['id'])
        if not entry:
            continue
        # A newer live collector result supersedes this frozen repair.
        source = row.get('name_source')
        if isinstance(source, dict) and source.get('kind') == 'official_page_title' and source.get('requested_at') and datetime.fromisoformat(source['requested_at']) > datetime.fromisoformat(entry['requested_at']):
            continue
        old = row.get('name')
        if old != entry['name']:
            row.setdefault('name_before_title_repair', old)
        row.update(name=entry['name'], source_url=entry['url'], name_source=dict(
            kind='official_page_title', url=entry['url'], title=entry['title'],
            sha256=entry['sha256'], requested_at=entry['requested_at']))
        # Classification must use the page's full title, including its suffix.
        from goodsdex.accessories import classify
        row['is_accessory'] = classify(row)['accessory']
        if row['is_accessory']:
            row['kind'] = 'accessory'
        elif row.get('kind') == 'accessory':
            row['kind'] = 'machine'
    return result
