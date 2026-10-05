#!/usr/bin/env python3
"""Check the requirement registry (specs/INDEX.md) against executable spec labels.

Format and rules: references/specs-contract.md. Exit 0 = consistent, 1 = findings, 2 = bad input.
"""
import argparse
from pathlib import Path
import re
import sys

COLUMNS = ['ID', 'Status', 'Behavior', 'Verify', 'Evidence', 'Origin']
ID = re.compile(r'^(AC|QR|OBS)-\d+$')
VERIFY = ('spec', 'static', 'contract', 'eval')
ORIGIN = re.compile(r'^(PRD|delta|OBS|deviation:OBS-\d+)$')
# A label is a quoted string literal in code: "req:AC-001" / 'req:AC-001'.
LABEL = re.compile(r'''["']req:((?:AC|QR|OBS)-\d+)["']''')
COMMENT = re.compile(r'^\s*(#|//|--|/\*|\*|<!--|;)')


def parse_index(text):
    """Return rows of the first Markdown table whose header is COLUMNS."""
    lines = [l.strip() for l in text.splitlines()]
    cells = lambda l: [c.strip() for c in l.strip('|').split('|')]
    for i, line in enumerate(lines):
        if line.startswith('|') and cells(line) == COLUMNS:
            rows = []
            for row in lines[i + 2:]:
                if not row.startswith('|'):
                    break
                values = cells(row)
                if len(values) != len(COLUMNS):
                    raise ValueError(f'row has {len(values)} cells, expected {len(COLUMNS)}: {row}')
                rows.append(dict(zip(COLUMNS, values)))
            return rows
    raise ValueError('INDEX table with columns ' + ' | '.join(COLUMNS) + ' not found')


def scan_labels(spec_root, index_path):
    """Map requirement ID -> list of 'file:line' where a non-comment label references it."""
    found = {}
    for path in sorted(p for p in spec_root.rglob('*') if p.is_file() and p.resolve() != index_path):
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if COMMENT.match(line):
                continue
            for req in LABEL.findall(line):
                found.setdefault(req, []).append(f'{path.relative_to(spec_root)}:{number}')
    return found


def check(rows, labels):
    errors, seen = [], {}
    for row in rows:
        rid = row['ID']
        if not ID.match(rid):
            errors.append(f'{rid}: invalid ID'); continue
        if rid in seen:
            errors.append(f'{rid}: duplicate ID'); continue
        seen[rid] = row
        if row['Status'] not in ('active', 'retired'):
            errors.append(f'{rid}: status must be active or retired')
        if row['Verify'] not in VERIFY:
            errors.append(f'{rid}: verify must be one of {", ".join(VERIFY)}')
        if not row['Behavior']:
            errors.append(f'{rid}: behavior required')
        if not ORIGIN.match(row['Origin']):
            errors.append(f'{rid}: origin must be PRD, delta, OBS or deviation:OBS-n')
        if row['Status'] != 'active':
            continue
        if row['Verify'] == 'spec':
            behavior = row['Behavior'].lower()
            if 'when' not in behavior or 'then' not in behavior:
                errors.append(f'{rid}: spec-verified behavior must state When and Then')
            if rid not in labels:
                errors.append(f'{rid}: active, no executable spec carries "req:{rid}"')
        elif not row['Evidence']:
            errors.append(f'{rid}: {row["Verify"]} verification needs an evidence reference')
    for rid, where in sorted(labels.items()):
        if rid not in seen:
            errors.append(f'{where[0]}: label req:{rid} not in INDEX')
        elif seen[rid]['Status'] == 'retired':
            errors.append(f'{where[0]}: label req:{rid} points to a retired requirement')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, default=Path('specs/INDEX.md'))
    parser.add_argument('--specs', type=Path, default=Path('specs'))
    args = parser.parse_args(argv)
    try:
        rows = parse_index(args.index.read_text(encoding='utf-8'))
        labels = scan_labels(args.specs, args.index.resolve())
    except (OSError, UnicodeError, ValueError) as exc:
        print(f'INPUT ERROR: {exc}', file=sys.stderr)
        return 2
    errors = check(rows, labels)
    for error in errors:
        print(f'FAIL: {error}', file=sys.stderr)
    if not errors:
        active = sum(r['Status'] == 'active' for r in rows)
        print(f'PASS: {active} active requirements traced')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
