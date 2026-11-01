#!/usr/bin/env python3
"""Offline Text to Dialogue REST payload preflight; no network, audio or account certification."""
import argparse
import json
from pathlib import Path

from cue_qc import effects_errors, present


def inspect(payload, output_format=None):
    errors = []
    if not isinstance(payload, dict):
        return ['Expected a Text to Dialogue REST payload object']
    if payload.get('model_id') not in ('eleven_v3', 'eleven_v4'):
        errors.append('Pin model_id explicitly to the approved eleven_v3 or eleven_v4; do not rely on the v3 API default or use Turbo REST')
    inputs = payload.get('inputs')
    if not isinstance(inputs, list) or not inputs:
        errors.append('inputs must be a nonempty list')
    else:
        total, voices = 0, set()
        for item in inputs:
            if not isinstance(item, dict) or not present(item.get('text')) or not present(item.get('voice_id')):
                errors.append('Each input requires nonempty text and a real assigned voice_id')
                continue
            total += len(item['text'])
            voices.add(item['voice_id'])
        if total > 2000:
            errors.append('Reliable-request policy: total inputs[].text exceeds 2000 characters including tags; split at performance boundaries without rewriting')
        if len(voices) > 10:
            errors.append('Text to Dialogue supports at most 10 unique voice IDs per request')
    for field in ('previous_text', 'future_text'):
        value = payload.get(field)
        if value is not None and (not isinstance(value, str) or len(value) > 100):
            errors.append(f'{field} must be null or a string of at most 100 characters')
    for field in ('previous_request_ids', 'next_request_ids'):
        value = payload.get(field)
        if value is not None and (not isinstance(value, list) or len(value) > 3 or any(not present(x) for x in value)):
            errors.append(f'{field} must be null or at most 3 nonempty request IDs')
    locators = payload.get('pronunciation_dictionary_locators')
    if locators is not None and (not isinstance(locators, list) or len(locators) > 3):
        errors.append('At most 3 pronunciation dictionary locators per request')
    errors.extend(effects_errors(payload.get('audio_effects'), output_format))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('payload', type=Path)
    parser.add_argument('--output-format', help='Actual query output_format, separate from JSON body')
    args = parser.parse_args()
    try:
        payload = json.loads(args.payload.read_text(encoding='utf-8'))
        errors = inspect(payload, args.output_format)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({'errors': errors, 'scope': 'Offline bounded REST payload checks only; no model-specific context, target, voice, plan or audio verification'}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
