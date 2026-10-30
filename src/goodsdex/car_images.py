"""Historical image provenance guard, shared by publication and grouping."""
from urllib.parse import urlsplit

IMAGE_FIELDS = ('image_source', 'image_source_type', 'image_source_url',
                'image_captured_at', 'image_note')


def validate_historical_image(row):
    if row.get('image') is None:
        return
    source = row.get('image_source_type')
    if row.get('image_source', source) != source:
        raise ValueError('Historical image source fields disagree')
    if source == 'official':
        return
    if source == 'official_archive':
        url = urlsplit(row.get('image_source_url') or '')
        if url.scheme == 'https' and url.hostname == 'web.archive.org' and not url.username and not url.password:
            return
        raise ValueError('Historical official_archive image requires https://web.archive.org image_source_url')
    raise ValueError('Historical image must be official, verified official_archive or null')
