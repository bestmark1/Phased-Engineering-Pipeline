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
# A label is a string literal in code that starts with req:<ID>: "req:AC-001", 'req:AC-001 shows name'.
LABEL = re.compile(r'req:((?:AC|QR|OBS)-\d+)(?=\s|$)')
# Spec files are test code; data, fixtures and prose never carry labels.
CODE_SUFFIXES = {'.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java', '.kt', '.kts',
                 '.rb', '.php', '.cs', '.swift', '.scala', '.ex', '.exs', '.dart', '.lua', '.hs', '.clj', '.sh'}
LINE_STARTS = {'.lua': ('--',), '.hs': ('--',)}
BLOCKS = {'.lua': [('--[[', ']]')], '.hs': [('{-', '-}')], '.py': [('"""', '"""'), ("'''", "'''")]}
COMMON_BLOCKS = [('/*', '*/'), ('<!--', '-->')]


def literals(lines, suffix=''):
    """Yield (line number, content) of every single-line string literal outside comments.
    Comments: //, #, block /* */ and <!-- -->, plus per-language -- / --[[ ]] / {- -} and Python
    docstrings (treated as comments: a label there is documentation, not a label)."""
    blocks = BLOCKS.get(suffix, []) + COMMON_BLOCKS
    starts = ('//', '#') + LINE_STARTS.get(suffix, ())
    closing = None
    for number, line in enumerate(lines, 1):
        i = 0
        if not closing and line.lstrip().startswith(('*', ';')):  # block-comment continuation, Lisp comment
            continue
        while i < len(line):
            if closing:
                end = line.find(closing, i)
                if end < 0:
                    break
                i, closing = end + len(closing), None
                continue
            opener = next(((o, c) for o, c in blocks if line.startswith(o, i)), None)
            if opener:
                i, closing = i + len(opener[0]), opener[1]
                continue
            if line.startswith(starts, i):
                break
            ch = line[i]
            if ch in '"\'`':
                j, content = i + 1, []
                while j < len(line) and line[j] != ch:
                    if line[j] == '\\':
                        content.append(line[j + 1:j + 2]); j += 2; continue
                    content.append(line[j]); j += 1
                if j < len(line):  # closed on this line
                    yield number, ''.join(content)
                i = j + 1
                continue
            i += 1


def parse_index(text):
    """Return rows of the first Markdown table whose header is COLUMNS."""
    lines = [l.strip() for l in text.splitlines()]
    cells = lambda l: [c.strip() for c in l.strip('|').split('|')]
    for i, line in enumerate(lines):
        if line.startswith('|') and cells(line) == COLUMNS:
            separator = lines[i + 1] if i + 1 < len(lines) else ''
            if not (separator.startswith('|') and all(re.fullmatch(r':?-{3,}:?', c) for c in cells(separator))):
                raise ValueError('INDEX table: header must be followed by a |---| separator row')
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
    support = spec_root / 'support'
    for path in sorted(p for p in spec_root.rglob('*') if p.is_file() and p.resolve() != index_path):
        if path.suffix.lower() not in CODE_SUFFIXES or support in path.parents:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        for number, content in literals(text.splitlines(), path.suffix.lower()):
            match = LABEL.match(content)
            if match:
                found.setdefault(match.group(1), []).append(f'{path.relative_to(spec_root)}:{number}')
    return found


def check(rows, labels, final=False):
    """final=True: initiative completion — no requirement may still be `planned`."""
    errors, seen = [], {}
    for row in rows:
        rid = row['ID']
        if not ID.match(rid):
            errors.append(f'{rid}: invalid ID'); continue
        if rid in seen:
            errors.append(f'{rid}: duplicate ID'); continue
        seen[rid] = row
        if row['Status'] not in ('active', 'planned', 'retired'):
            errors.append(f'{rid}: status must be active, planned or retired')
        if row['Verify'] not in VERIFY:
            errors.append(f'{rid}: verify must be one of {", ".join(VERIFY)}')
        if not row['Behavior']:
            errors.append(f'{rid}: behavior required')
        if not ORIGIN.match(row['Origin']):
            errors.append(f'{rid}: origin must be PRD, delta, OBS or deviation:OBS-n')
        if final and row['Status'] == 'planned':
            errors.append(f'{rid}: still planned at initiative completion; implement it, or the owner moves it '
                          f'out of scope (retire with a reason / a later initiative)')
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
        elif seen[rid]['Status'] == 'planned':
            errors.append(f'{where[0]}: label req:{rid} points to a planned requirement; '
                          f'set it active in the same commit as its spec')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, default=Path('specs/INDEX.md'))
    parser.add_argument('--specs', type=Path, default=Path('specs'))
    parser.add_argument('--final', action='store_true',
                        help='initiative completion: fail on any planned requirement')
    args = parser.parse_args(argv)
    try:
        rows = parse_index(args.index.read_text(encoding='utf-8'))
        labels = scan_labels(args.specs, args.index.resolve())
    except (OSError, UnicodeError, ValueError) as exc:
        print(f'INPUT ERROR: {exc}', file=sys.stderr)
        return 2
    errors = check(rows, labels, final=args.final)
    for error in errors:
        print(f'FAIL: {error}', file=sys.stderr)
    if not errors:
        active = sum(r['Status'] == 'active' for r in rows)
        planned = sum(r['Status'] == 'planned' for r in rows)
        print(f'PASS: {active} active requirements traced; {planned} planned')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
