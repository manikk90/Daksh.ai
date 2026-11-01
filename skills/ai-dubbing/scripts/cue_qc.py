#!/usr/bin/env python3
"""Offline cue preflight with revision-aware review metadata. Never certifies acting or dialect."""
import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

TAG = re.compile(r'\[([^\[\]]*)\]')
REVIEW_STAGES = ('text', 'native', 'acting', 'sync', 'technical')
INPUT_FIELDS = ('cue_id', 'character_id', 'language', 'regional_variety', 'track_id',
                'source_text', 'approved_localized_text', 'render_text', 'word_lock',
                'route', 'model_id', 'voice_id', 'voice_settings', 'pronunciation_version',
                'casting_version', 'start_s', 'end_s', 'allowed_overhang_s', 'overlap_group',
                'measured_duration_s', 'approved_take_id', 'audio_sha256', 'capability_evidence')


def tokens(text):
    text = unicodedata.normalize('NFC', text)
    return ''.join(c if unicodedata.category(c)[0] in 'LMN' else ' ' for c in text).casefold().split()


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def present(value):
    return isinstance(value, str) and bool(value.strip())


def effects_errors(effects, output_format=None):
    """Narrow documented effects/format check, not a full provider schema validator."""
    if effects is None:
        return []
    if not isinstance(effects, dict):
        return ['audio_effects must be an object or null']
    errors = []
    for field in ('send_level', 'pan'):
        if field in effects and not finite_number(effects[field]):
            errors.append(f'audio_effects.{field} must be a finite number')
    if errors:
        return errors
    stereo = (present(effects.get('environment_id')) and effects.get('send_level', 0) > 0
              or effects.get('pan', 0) != 0)
    if stereo and isinstance(output_format, str) and output_format.startswith(('pcm_', 'ulaw_', 'alaw_')):
        errors.append('Stereo reverb/pan is incompatible with pcm_*, ulaw_* and alaw_* output formats')
    return errors


def fingerprint(data, cue):
    cue_index = {c.get('cue_id'): c for c in data.get('cues', [])
                 if isinstance(c, dict) and present(c.get('cue_id'))}
    refs = cue.get('context_ref_ids', [])
    context = []
    if isinstance(refs, list):
        for ref in refs:
            other = cue_index.get(ref) if isinstance(ref, str) else None
            context.append({'ref': ref, 'input': {k: other.get(k) for k in
                            ('render_text', 'voice_id', 'model_id', 'request_id')} if other else None})
    payload = {'project_id': data.get('project_id'),
               'picture_segment_version': cue.get('picture_segment_version') or data.get('picture_version'),
               'cue': {key: cue.get(key) for key in INPUT_FIELDS},
               'context': context, 'generation_context': cue.get('generation_context')}
    # Preserve existing fingerprints when optional execution records are absent.
    execution = {key: cue[key] for key in ('api_endpoint', 'audio_effects', 'output_format', 'request_options')
                 if key in cue}
    if execution:
        payload['execution_options'] = execution
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def inspect(data, phase='draft', root=None):
    findings = []
    def add(level, cue, message, gate=False):
        findings.append({'level': level, 'cue_id': cue, 'message': message, 'release_blocker': gate or level == 'error'})
    def gate(cue, message):
        add('error' if phase == 'release' else 'warning', cue, message, True)
    if not isinstance(data, dict) or not isinstance(data.get('cues'), list):
        add('error', None, 'Expected object with cues array')
        return findings
    if not data['cues']:
        add('error', None, 'Empty cue list cannot pass production preflight')
        return findings
    for field in ('project_id', 'picture_version', 'source_version'):
        if not present(data.get(field)):
            gate(None, f'Missing {field}; release version is not pinned')
    ids, intervals = set(), {}
    for i, cue in enumerate(data['cues']):
        if not isinstance(cue, dict):
            add('error', str(i), 'Cue must be an object')
            continue
        cid = cue.get('cue_id')
        if not present(cid):
            add('error', str(i), 'Missing nonempty cue_id')
            cid = str(i)
        if cid in ids:
            add('error', cid, 'Duplicate cue_id')
        ids.add(cid)
        for field in ('character_id', 'language', 'track_id', 'route', 'model_id'):
            if not present(cue.get(field)):
                gate(cid, f'Missing {field}; cue routing is incomplete')
        refs = cue.get('context_ref_ids', [])
        known_ids = {c.get('cue_id') for c in data['cues']
                     if isinstance(c, dict) and present(c.get('cue_id'))}
        if not isinstance(refs, list) or any(not present(ref) or ref not in known_ids or ref == cid for ref in refs):
            add('error', cid, 'context_ref_ids must name existing other cues')
        rendered, approved = cue.get('render_text'), cue.get('approved_localized_text')
        if not present(rendered) or not present(approved):
            add('error', cid, 'Approved and rendering text must be nonempty strings')
            continue
        if not isinstance(cue.get('word_lock'), bool):
            add('error', cid, 'word_lock must be a boolean, not a string or number')
        clean = TAG.sub('', rendered)
        if '[' in clean or ']' in clean:
            add('error', cid, 'Malformed or nested square-bracket tag')
        if not tokens(clean):
            add('error', cid, 'Rendering contains no spoken dialogue')
        for match in TAG.finditer(rendered):
            tag = match.group(1)
            letters = [c for c in tag if unicodedata.category(c).startswith('L')]
            if not letters or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in letters):
                add('error', cid, 'Tags must contain English direction only')
            if re.search(r'\b(eyes? (widen|blink)|eyebrows? (lift|raise)|head (tilt|turn))\b', tag, re.I):
                gate(cid, 'Visual-only tag found; express audible consequence or use Director handoff')
        if cue.get('word_lock') is True and tokens(clean) != tokens(approved):
            add('error', cid, 'Locked spoken words changed, added, omitted or reordered')
        start, end = cue.get('start_s'), cue.get('end_s')
        valid_time = finite_number(start) and finite_number(end) and start >= 0 and end > start
        if not valid_time:
            add('error', cid, 'Invalid start/end timing')
        else:
            key = (str(cue.get('language')), str(cue.get('track_id')))
            intervals.setdefault(key, []).append((start, end, cid, cue.get('overlap_group')))
            duration, tolerance = cue.get('measured_duration_s'), cue.get('allowed_overhang_s', 0)
            if not finite_number(tolerance) or tolerance < 0:
                add('error', cid, 'Invalid allowed_overhang_s')
            elif duration is None:
                gate(cid, 'Audio duration unmeasured; sync not evaluated')
            elif not finite_number(duration) or duration <= 0:
                add('error', cid, 'Invalid measured_duration_s')
            elif duration > end - start + tolerance:
                gate(cid, f'Measured audio exceeds slot by {duration-(end-start):.3f}s')
        settings = cue.get('voice_settings', {})
        for message in effects_errors(cue.get('audio_effects'), cue.get('output_format')):
            add('error', cid, message)
        if not isinstance(settings, dict):
            add('error', cid, 'voice_settings must be an object')
        else:
            for key in ('stability', 'similarity_boost'):
                value = settings.get(key)
                if key in settings and (not finite_number(value) or not 0 <= value <= 1):
                    add('error', cid, f'{key} must be a number from 0 to 1')
            if cue.get('model_id') in ('eleven_v4', 'eleven_v4_turbo'):
                for key in ('speed', 'style', 'style_exaggeration'):
                    if key in settings:
                        add('error', cid, f'Unsupported v4 recipe setting: {key}; verify current surface')
        if not present(cue.get('voice_id')):
            gate(cid, 'Voice is unassigned; generation is not ready')
        capability = cue.get('capability_evidence', {})
        if not isinstance(capability, dict):
            add('error', cid, 'capability_evidence must be an object')
        elif (capability.get('status') != 'confirmed' or capability.get('account_verified') is not True
              or not present(capability.get('checked_at')) or not present(capability.get('reference'))):
            gate(cid, 'Selected route/target/account capability has not been confirmed')
        if not present(cue.get('approved_take_id')):
            gate(cid, 'No approved take selected')
        audio_hash = cue.get('audio_sha256')
        if not isinstance(audio_hash, str) or not re.fullmatch(r'[0-9a-f]{64}', audio_hash):
            gate(cid, 'Missing valid SHA-256 for selected audio')
        path = cue.get('audio_path')
        if not present(path):
            gate(cid, 'Selected audio artifact is missing')
        elif root is None:
            gate(cid, 'Audio file availability/hash was not checked')
        else:
            audio = Path(path)
            if not audio.is_absolute():
                audio = Path(root) / audio
            try:
                if not audio.is_file():
                    gate(cid, 'Selected audio file is unavailable')
                elif isinstance(audio_hash, str) and digest_file(audio) != audio_hash:
                    gate(cid, 'Audio bytes do not match selected take hash')
            except OSError:
                gate(cid, 'Selected audio file cannot be read')
        reviews = cue.get('reviews', {})
        if not isinstance(reviews, dict):
            add('error', cid, 'reviews must be an object')
        else:
            current = fingerprint(data, cue)
            for stage in REVIEW_STAGES:
                review = reviews.get(stage, {})
                if not isinstance(review, dict) or review.get('status') != 'approved':
                    gate(cid, f'{stage} review is pending')
                elif review.get('fingerprint') != current:
                    gate(cid, f'{stage} approval is stale after an input/take/version change')
                elif not present(review.get('reviewer')) or not present(review.get('evidence_ref')):
                    gate(cid, f'{stage} review has no reviewer/evidence record')
    for group in intervals.values():
        active = []
        for item in sorted(group):
            active = [old for old in active if old[1] > item[0]]
            for old in active:
                intentional = present(item[3]) and item[3] == old[3]
                if not intentional:
                    gate(item[2], f'Unmarked same-track overlap with {old[2]}')
            active.append(item)
    return findings


def report(data, phase='draft', root=None):
    findings = inspect(data, phase, root)
    hashes = {}
    if isinstance(data, dict) and isinstance(data.get('cues'), list):
        for i, cue in enumerate(data['cues']):
            if isinstance(cue, dict):
                key = cue.get('cue_id')
                hashes[key if present(key) else str(i)] = fingerprint(data, cue)
    blockers = sum(f['release_blocker'] for f in findings)
    return {'phase': phase, 'errors': sum(f['level'] == 'error' for f in findings),
            'release_blockers': blockers, 'release_metadata_complete': blockers == 0,
            'fingerprints': hashes, 'findings': findings,
            'scope': 'Metadata, text, timing and file-integrity checks only; no acting, dialect or lip-sync certification'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--phase', choices=('draft', 'release'), default='draft')
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding='utf-8'))
        result = report(data, args.phase, args.manifest.parent)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
