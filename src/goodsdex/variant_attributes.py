"""Replay reviewed variant conclusions verbatim; unknown groups never annotate rows."""
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

DEFAULT_SOURCE = Path(__file__).resolve().parents[2] / 'data/variant-attributes.json'
SOURCE = 'variant-attributes-20261104'


def apply_variant_attributes(rows, source=DEFAULT_SOURCE):
    document = json.loads(Path(source).read_text())
    members = {}
    for group in document['groups']:
        if group['verdict'] == 'unknown':
            continue
        for member in group['members']:
            if not member.get('attrs'):
                continue
            value = (member['attrs'], group['confidence'])
            if group['confidence'] not in ('high', 'medium'):
                raise ValueError('Unsupported variant confidence')
            if member['id'] in members and members[member['id']] != value:
                raise ValueError(f"Conflicting variant conclusions: {member['id']}")
            members[member['id']] = value
    result = []
    tagged = 0
    for row in rows:
        row = dict(row)
        if row['id'] in members:
            attrs, confidence = members[row['id']]
            row.update(attrs=deepcopy(attrs), attrs_source=SOURCE, attrs_confidence=confidence)
            tagged += 1
        result.append(row)
    return result, dict(groups=len(document['groups']), members_tagged=tagged,
                       by_kind=dict(Counter(g['verdict'] for g in document['groups'])), source=SOURCE)
