#!/usr/bin/env python3
"""Compare installed skill copies with dist/<skill>.skill. Read-only; archives are read in memory.

Exit codes: 0 every pair matches, 1 any MISSING/DIFFERS, 2 unreadable dist.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile

DIST = Path(__file__).resolve().parent.parent / 'dist'
LIMIT = 10


def default_roots():
    roots = [Path.home() / '.claude' / 'skills', Path.home() / '.codex' / 'skills']
    env = os.environ.get('CLAUDE_CONFIG_DIR')
    if env and Path(env).expanduser() != Path.home() / '.claude':
        roots.append(Path(env).expanduser() / 'skills')
    return roots


def dist_files(archive):
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive.read_bytes()), mode='r:gz') as tar:
        for member in tar:
            if member.isfile():
                rel = member.name[2:] if member.name.startswith('./') else member.name
                files[rel] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
    return files


def ignored(rel):
    return '__pycache__' in rel.split('/') or rel.endswith('.pyc')


def installed_files(directory):
    files = {}
    for base, dirs, names in os.walk(directory, followlinks=False):
        for name in names:
            path = Path(base) / name
            rel = path.relative_to(directory).as_posix()
            if ignored(rel) or path.is_symlink() or not path.is_file():
                continue
            files[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def compare(expected, directory):
    if not directory.is_dir():
        return 'MISSING', []
    actual = installed_files(directory)
    diffs = [('only-in-dist', r) for r in sorted(expected.keys() - actual.keys())]
    diffs += [('only-installed', r) for r in sorted(actual.keys() - expected.keys())]
    diffs += [('content', r) for r in sorted(expected.keys() & actual.keys()) if expected[r] != actual[r]]
    return ('DIFFERS', diffs) if diffs else ('MATCH', [])


def check(roots, dist):
    archives = sorted(Path(dist).glob('*.skill'))
    if not archives:
        raise ValueError(f'no *.skill files in {dist}')
    results = []
    for archive in archives:
        expected = dist_files(archive)
        for root in roots:
            status, diffs = compare(expected, root / archive.stem)
            results.append({'status': status, 'root': str(root), 'skill': archive.stem,
                            'diffs': [{'kind': k, 'path': p} for k, p in diffs[:LIMIT]],
                            'diff_total': len(diffs)})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', action='append', type=Path, help='skill root (repeatable)')
    parser.add_argument('--dist', type=Path, default=DIST)
    parser.add_argument('--json', action='store_true')
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    roots = args.root or default_roots()
    try:
        results = check(roots, args.dist)
    except (OSError, tarfile.TarError, ValueError) as exc:
        print(f'cannot read dist: {exc}', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f'{r["status"]:<8}{r["root"]}/{r["skill"]}')
            for d in r['diffs']:
                print(f'    {d["kind"]}: {d["path"]}')
            if r['diff_total'] > len(r['diffs']):
                print(f'    ... {r["diff_total"] - len(r["diffs"])} more')
    return 0 if all(r['status'] == 'MATCH' for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
