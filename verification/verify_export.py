#!/usr/bin/env python3
"""Verify this exported archive's file hashes, source snapshots and nested ZIPs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / 'verification/FILE_HASHES.json'
    if not manifest_path.is_file():
        return ['FILE_HASHES.json was not found; provide the extracted bundle root.']
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return [f'Cannot load hash manifest: {exc}']
    expected = {r['path'] for r in manifest['files']}
    for record in manifest['files']:
        relative = Path(record['path'])
        if relative.is_absolute() or '..' in relative.parts:
            errors.append('Unsafe manifest member: ' + str(relative))
            continue
        path = root / relative
        if not path.is_file():
            errors.append('Missing: ' + str(relative))
        elif file_hash(path) != record['sha256']:
            errors.append('Hash mismatch: ' + str(relative))
    for path in root.rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts or path.name == '.DS_Store':
            continue
        relative = path.relative_to(root).as_posix()
        if relative not in expected and relative != 'verification/FILE_HASHES.json':
            errors.append('Unexpected file: ' + relative)
    try:
        records = json.loads((root/'mapping/source_files.json').read_text(encoding='utf-8'))['source_files']
        for record in records:
            path = root/record['archive_path']
            if not path.is_file() or file_hash(path) != record['sha256']:
                errors.append('Original-source hash mismatch: '+record['archive_path'])
        for path in sorted((root/'skill_packages').glob('*/skill.zip')):
            with ZipFile(path) as archive:
                bad = archive.testzip()
                if bad:
                    errors.append('Nested ZIP CRC error: '+str(path)+': '+bad)
                entries = [n for n in archive.namelist() if n.endswith('/SKILL.md')]
                if len(entries) != 1:
                    errors.append('Not a single-skill archive: '+str(path))
    except (OSError, ValueError, KeyError) as exc:
        errors.append('Source/package validation error: '+str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    issues = verify(root)
    if issues:
        print(json.dumps({'status':'FAIL','issues':issues}, indent=2))
        return 1
    count = len(json.loads((root/'verification/FILE_HASHES.json').read_text())['files'])
    print(json.dumps({'status':'PASS','hashed_files':count,'root':str(root)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
