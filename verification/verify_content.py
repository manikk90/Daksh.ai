#!/usr/bin/env python3
"""Verify the export's bounded documentation inclusion checks, not agent behavior."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def verify(root: Path) -> list[str]:
    """Return source/anchor/marker omissions in an extracted audited bundle."""
    errors: list[str] = []
    try:
        modules = json.loads((root/'audit/INLINE_MODULES.json').read_text(encoding='utf-8'))
        for record in modules:
            source = root/record['source_path']
            dossier = root/record['dossier']
            if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != record['source_sha256']:
                errors.append('Source mismatch: '+record['source_path'])
            if not dossier.is_file() or 'id="'+record['anchor']+'"' not in dossier.read_text(encoding='utf-8'):
                errors.append('Module section absent: '+record['source_path'])
        checks = json.loads((root/'audit/CONTENT_CHECKS.json').read_text(encoding='utf-8'))
        for check in checks:
            text = (root/check['file']).read_text(encoding='utf-8')
            for marker in check['required_text']:
                if marker not in text:
                    errors.append(check['id']+': missing '+marker)
    except (OSError, ValueError, KeyError) as exc:
        errors.append('Cannot read audit data: '+str(exc))
    return errors


def main() -> int:
    """Run bounded documentation verification on the chosen export root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    issues = verify(Path(args.root).resolve())
    print(json.dumps({'status': 'FAIL' if issues else 'PASS_TEXT_INCLUSION', 'issues': issues, 'not_proven': ['exhaustive chat coverage','agent execution','media quality','live installation']}, indent=2))
    return 1 if issues else 0


if __name__ == '__main__':
    raise SystemExit(main())
