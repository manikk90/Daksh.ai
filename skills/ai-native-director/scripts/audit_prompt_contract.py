#!/usr/bin/env python3
"""Check literal prompt IDs, asset tags and supplied dialogue; never certify media.

Input: {"shots": [{"shot_id": "@s1p1s1", "prompt": "...",
"required_tags": [], "allowed_tags": [], "exact_dialogue": []}]}.
Pass only exact, task-approved visible tags in allowed_tags. The shot ID is separate.
Supply expectations from source/locks, not by extracting them from the draft itself.
"""
import argparse
import json
import re
from pathlib import Path

TAG = re.compile(r"(?<![\w@])@[\w][\w.\-]*(?:'[\w]+)?", re.UNICODE)


def tags_in(prompt):
    # Strip prose punctuation and possessive endings; preserve tag case and suffixes.
    return {m.group().split("'")[0].rstrip('.') for m in TAG.finditer(prompt)}


def audit(data):
    if not isinstance(data, dict) or not isinstance(data.get('shots'), list) or not data['shots']:
        raise ValueError('Nonempty shots list required')
    seen = set()
    findings = []
    for shot in data['shots']:
        if not isinstance(shot, dict):
            raise ValueError('Each shot must be an object')
        sid, prompt = shot.get('shot_id'), shot.get('prompt')
        if not isinstance(sid, str) or not sid.startswith('@') or sid in seen:
            raise ValueError('Unique exact shot_id required')
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f'Prompt required for {sid}')
        seen.add(sid)
        values = {}
        for field in ['required_tags', 'allowed_tags', 'exact_dialogue']:
            value = shot.get(field)
            if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
                raise ValueError(f'{field} list required for {sid}')
            if len(value) != len(set(value)):
                raise ValueError(f'Duplicate {field} expectation in {sid}')
            values[field] = value
        required, allowed = set(values['required_tags']), set(values['allowed_tags'])
        if not required.issubset(allowed):
            raise ValueError(f'Required tags must be allowed for {sid}')
        for tag in allowed:
            if not isinstance(tag, str) or tags_in(tag) != {tag} or not TAG.fullmatch(tag) or tag == sid:
                raise ValueError(f'Invalid exact asset tag expectation for {sid}: {tag}')
        actual = tags_in(prompt)
        if sid not in actual:
            findings.append({'shot_id': sid, 'issue': 'missing_shot_id', 'value': sid})
        actual.discard(sid)
        for tag in sorted(required - actual):
            findings.append({'shot_id': sid, 'issue': 'missing_tag', 'value': tag})
        for tag in sorted(actual - allowed):
            findings.append({'shot_id': sid, 'issue': 'unexpected_tag', 'value': tag})
        cursor = 0
        for line in values['exact_dialogue']:
            position = prompt.find(line, cursor)
            if position < 0:
                findings.append({'shot_id': sid, 'issue': 'missing_or_reordered_exact_dialogue', 'value': line})
            else:
                cursor = position + len(line)
    return {'literal_contract': 'FAIL' if findings else 'PASS', 'shots_checked': len(seen),
            'findings': findings,
            'limits': 'Literal text only. Does not establish complete dialogue, semantics, source approval, asset binding, camera, anatomy or media quality.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('contract', type=Path)
    args = parser.parse_args()
    try:
        result = audit(json.loads(args.contract.read_text()))
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({'literal_contract': 'INVALID', 'error': str(error)}))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return int(result['literal_contract'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
