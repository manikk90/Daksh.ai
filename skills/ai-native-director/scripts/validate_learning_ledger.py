#!/usr/bin/env python3
"""Validate learning records and adoption gates; never certify media quality."""
import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def evidence(value):
    return isinstance(value, list) and bool(value) and all(text(item) for item in value)


def validate(data):
    require(isinstance(data, dict) and data.get('schema_version') == 1,
            'Supported learning schema required')
    require(data.get('skill') == 'ai-native-director', 'Wrong skill ledger')
    require(type(data.get('revision')) is int and data['revision'] >= 1, 'Positive ledger revision required')
    scheduler = data.get('scheduler', {})
    require(isinstance(scheduler, dict), 'Scheduler must be an object')
    require(scheduler.get('status') in {'requested', 'configured'}, 'Invalid scheduler state')
    require(scheduler.get('cadence') == 'P1D' and scheduler.get('timezone') == 'Asia/Kolkata',
            'Nightly chat review requires daily Asia/Kolkata cadence')
    require(scheduler.get('coordinator') == 'daksh'
            and scheduler.get('mode') == 'one_coordinator_with_weekly_branch',
            'Use one Daksh coordinator, not individual specialist timers')
    daily = scheduler.get('daily_chat_review', {})
    weekly = scheduler.get('weekly_research', {})
    require(isinstance(daily, dict) and daily.get('cadence') == 'P1D'
            and daily.get('not_before') == '23:00', 'Nightly chat review must start at or after 23:00')
    require(isinstance(weekly, dict) and weekly.get('day') == 'SU'
            and weekly.get('not_before') == '23:00'
            and weekly.get('mode') == 'conditional_branch_in_same_daily_automation',
            'Internet research must be the Sunday 23:00 branch of the same daily task')
    require(text(scheduler.get('schedule')), 'Requested or confirmed daily schedule required')
    rule = next((line for line in scheduler['schedule'].splitlines() if line.startswith('RRULE:')), '')
    parts = set(rule.removeprefix('RRULE:').split(';'))
    require('FREQ=DAILY' in parts and not any(part.startswith('BYDAY=') for part in parts)
            and all(part == 'INTERVAL=1' for part in parts if part.startswith('INTERVAL=')),
            'Coordinator trigger must run every day')
    start = next((line for line in scheduler['schedule'].splitlines() if line.startswith('DTSTART')), '')
    require('TZID=Asia/Kolkata' in start and start.endswith('T230000'),
            'Coordinator schedule must use the confirmed 23:00 Asia/Kolkata start')
    if scheduler['status'] == 'configured':
        require(text(scheduler.get('automation_id')) and scheduler.get('confirmation_pending') is False
                and type(scheduler.get('is_enabled')) is bool and text(scheduler.get('verified_on')),
                'Configured schedule requires observed identity, enabled state and verification date')
    else:
        require(scheduler.get('confirmation_pending') is True and scheduler.get('is_enabled') is not True,
                'Unconfirmed schedule must remain pending')
    checkpoint = data.get('research_checkpoint')
    require(isinstance(checkpoint, dict), 'Research checkpoint required')
    if checkpoint.get('last_successful_review'):
        date.fromisoformat(checkpoint['last_successful_review'])
    lessons = data.get('lessons')
    require(isinstance(lessons, list), 'Lessons list required')
    seen = {}
    for lesson in lessons:
        require(isinstance(lesson, dict), 'Lesson must be an object')
        lid = lesson.get('id')
        require(text(lid) and lid not in seen, 'Unique lesson ID required')
        require(type(lesson.get('version')) is int and lesson['version'] >= 1, f'Invalid version: {lid}')
        require(lesson.get('status') in {'active', 'pending', 'superseded', 'rejected'}, f'Invalid status: {lid}')
        for key in ['trigger', 'rule', 'boundary']:
            require(text(lesson.get(key)), f'{key} required: {lid}')
        scope = lesson.get('scope', {})
        require(scope.get('level') in {'global', 'project', 'scene', 'shot', 'tool'}, f'Invalid scope: {lid}')
        if scope['level'] in {'project', 'scene', 'shot'}:
            require(text(scope.get('project')), f'Project scope missing: {lid}')
        if scope['level'] in {'scene', 'shot'}:
            require(text(scope.get('scene')), f'Scene scope missing: {lid}')
        if scope['level'] == 'shot':
            require(text(scope.get('shot')), f'Shot scope missing: {lid}')
        if scope['level'] == 'tool':
            require(text(scope.get('tool')) and text(scope.get('interface')), f'Tool/interface scope missing: {lid}')
        source = lesson.get('source', {})
        require(source.get('type') in {'user_correction', 'qc_finding', 'official_documentation', 'original_research'},
                f'Invalid source type: {lid}')
        require(text(source.get('evidence')), f'Source evidence required: {lid}')
        validation = lesson.get('validation', {})
        require(validation.get('kind') in {'user_lock', 'syntax_or_contract', 'behavioral_text', 'visual', 'temporal', 'audio'},
                f'Validation kind required: {lid}')
        require(validation.get('status') in {'PASS', 'FAIL', 'PENDING'}, f'Invalid validation state: {lid}')
        if validation['status'] == 'PASS':
            require(evidence(validation.get('evidence')), f'Passed validation needs evidence: {lid}')
        cases = lesson.get('cases')
        require(isinstance(cases, list) and bool(cases), f'Failure and boundary case required: {lid}')
        require(all(isinstance(case, dict) and all(text(case.get(k)) for k in ['input', 'expected', 'boundary'])
                    for case in cases), f'Incomplete case: {lid}')
        research = source['type'] in {'official_documentation', 'original_research'}
        if research:
            url = urlparse(source.get('url', ''))
            require(url.scheme == 'https' and bool(url.hostname) and not url.username and not url.password,
                    f'Public source URL required: {lid}')
            date.fromisoformat(source.get('checked_on', ''))
        if lesson['status'] == 'active':
            require(validation['status'] != 'FAIL', f'Failed lesson cannot stay active: {lid}')
            if source['type'] == 'qc_finding':
                require(validation['status'] == 'PASS' and validation['kind'] != 'user_lock',
                        f'QC-derived learning needs a passed test: {lid}')
            if research:
                require(source.get('primary') is True and validation['status'] == 'PASS'
                        and validation['kind'] != 'user_lock', f'Research adoption lacks verified test: {lid}')
            if lesson.get('claims_quality_gain'):
                comparison = validation.get('comparison', {})
                require(validation['kind'] in {'visual', 'temporal', 'audio'} and validation['status'] == 'PASS'
                        and all(text(comparison.get(k)) for k in ['baseline', 'candidate', 'observed_result']),
                        f'Quality claim needs inspected comparison: {lid}')
        require(isinstance(lesson.get('supersedes'), list), f'Supersession list required: {lid}')
        seen[lid] = lesson
    for lid, lesson in seen.items():
        for old in lesson['supersedes']:
            require(old in seen and old != lid and seen[old]['status'] == 'superseded',
                    f'Supersession must identify an inactive old lesson: {lid}')
    pending = checkpoint.get('pending_candidates', [])
    require(isinstance(pending, list) and all(lid in seen and seen[lid]['status'] == 'pending' for lid in pending),
            'Pending checkpoint disagrees with lesson states')
    adopted = checkpoint.get('adopted_changes', [])
    require(isinstance(adopted, list) and all(lid in seen and seen[lid]['status'] == 'active' for lid in adopted),
            'Adopted checkpoint disagrees with active lessons')
    return {'contract': 'VALID', 'lessons': len(lessons),
            'note': 'Record consistency only; source authenticity and media quality require actual inspection.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.ledger.read_text()))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'contract': 'INVALID', 'error': str(error)}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
