#!/usr/bin/env python3
"""Validate project context and append observed metrics; no passive collection or cloud writes."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from statistics import median

METRICS = ('wall_time_seconds', 'source_reads', 'repeat_reads', 'correction_rounds',
           'accepted_shots', 'requested_shots', 'literal_cases',
           'expected_literal_results_matched', 'behavioral_text_cases', 'media_tests')


def check(condition, message):
    if not condition:
        raise ValueError(message)


def event_valid(event):
    check(isinstance(event, dict), 'Event must be an object')
    for key in ('run_id', 'kind', 'status'):
        check(isinstance(event.get(key), str) and event[key].strip(), f'{key} required')
    for key in METRICS:
        value = event.get(key)
        check(value is None or (type(value) in (int, float) and math.isfinite(value) and value >= 0), f'Invalid {key}')
        if key != 'wall_time_seconds' and value is not None:
            check(type(value) is int, f'{key} must be an observed integer count')
    for count, total in [('accepted_shots', 'requested_shots'),
                         ('expected_literal_results_matched', 'literal_cases'),
                         ('repeat_reads', 'source_reads')]:
        if event.get(count) is not None and event.get(total) is not None:
            check(event[count] <= event[total], f'{count} exceeds {total}')


def validate(data):
    check(isinstance(data, dict) and data.get('schema_version') == 1, 'Unknown project schema')
    check(isinstance(data.get('project_id'), str) and data['project_id'], 'Project ID required')
    check(type(data.get('record_revision')) is int and data['record_revision'] > 0,
          'Positive record revision required')
    chars = data.get('characters')
    check(isinstance(chars, list), 'Characters list required')
    ids, tags = set(), set()
    for character in chars:
        check(isinstance(character, dict), 'Character must be an object')
        cid, tag = character.get('character_id'), character.get('exact_identity_tag')
        check(isinstance(cid, str) and cid and cid not in ids, 'Duplicate/missing character ID')
        ids.add(cid)
        if tag is not None:
            check(isinstance(tag, str) and tag.startswith('@') and tag not in tags,
                  'Duplicate/invalid character tag')
            tags.add(tag)
        check(character.get('completeness') in ('PARTIAL', 'PENDING', 'COMPLETE'),
              'Profile completeness must be explicit')
        check(isinstance(character.get('unknown_fields'), list), 'Unknown fields must be explicit')
        check(character['completeness'] != 'COMPLETE' or not character['unknown_fields'],
              'Complete profile still contains unknown fields')
    events = data.get('performance_tracking', {}).get('entries')
    check(isinstance(events, list), 'Performance entries required')
    runs = set()
    for event in events:
        event_valid(event)
        check(event['run_id'] not in runs, 'Duplicate metrics run ID')
        runs.add(event['run_id'])
    return data


def summary(data):
    events = data['performance_tracking']['entries']
    durations = [e['wall_time_seconds'] for e in events if e.get('wall_time_seconds') is not None]
    return {'project_id': data['project_id'], 'record_revision': data['record_revision'],
            'character_records': len(data['characters']),
            'complete_profiles': sum(c['completeness'] == 'COMPLETE' for c in data['characters']),
            'logged_runs': len(events), 'measured_duration_runs': len(durations),
            'median_observed_wall_time_seconds': median(durations) if durations else None,
            'note': 'Structural/observed metrics only; no source, visual or cross-agent sync certification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('validate', 'summary', 'log-event'))
    parser.add_argument('record', type=Path)
    parser.add_argument('--event', type=Path)
    parser.add_argument('--expected-revision', type=int)
    args = parser.parse_args()
    try:
        data = validate(json.loads(args.record.read_text()))
        if args.command == 'log-event':
            check(args.event is not None and args.expected_revision == data['record_revision'],
                  'Event file and matching expected revision required')
            event = json.loads(args.event.read_text())
            event_valid(event)
            event.setdefault('observed_at', datetime.now(timezone.utc).isoformat())
            data['performance_tracking']['entries'].append(event)
            data['record_revision'] += 1
            data['updated_at'] = datetime.now(timezone.utc).isoformat()
            validate(data)
            # Editing in place retains any Library identity xattrs on the materialized file.
            args.record.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'structural_contract': 'VALID', **summary(data)}, ensure_ascii=False))
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'structural_contract': 'INVALID', 'error': str(error)}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
