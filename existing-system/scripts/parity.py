#!/usr/bin/env python3
"""Parity gate: run the frozen spec suite against a product commit and compare with the baseline.

  run      Check out <product-sha> in a temporary worktree, overlay the suite paths (default
           specs/) from <suite-sha>, run the project's spec command and record raw results.
           The command writes JSON {spec_id: {"outcome": "pass"|"fail", "observation": str}}
           to the path in $PARITY_RESULTS. Spec failures are data, not a runner error.
  compare  Verdict of a run against the baseline (references/parity.md): PASS, FAIL or UNKNOWN.

Exit codes: run 0 = record written, 2 = could not run. compare 0 = PASS, 1 = FAIL or UNKNOWN
(the verdict line says which; both block Done), 2 = unreadable or malformed input.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

OUTCOMES = ('pass', 'fail')


class InputError(Exception):
    pass


def git(repo, *args, **kw):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, **kw)


def safe_suite_paths(suite_paths):
    """Suite paths are repository-relative, normalized, inside the tree and never .git."""
    clean = []
    for rel in suite_paths:
        parts = Path(rel).parts
        # .git compared case-insensitively: on macOS/Windows .GIT is the same directory.
        if not rel or Path(rel).is_absolute() or '..' in parts or any(x.lower() == '.git' for x in parts) or rel in ('.', ''):
            raise InputError(f'suite path must be a relative path inside the repository: {rel!r}')
        clean.append(Path(*parts).as_posix())
    return clean


def run(repo, suite_sha, product_sha, command, environment, suite_paths=('specs',)):
    """Execute the suite frozen at suite_sha against product_sha; return the run record."""
    repo = Path(repo).resolve()
    suite_paths = safe_suite_paths(suite_paths)
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp) / 'tree'
        results = Path(tmp) / 'results.json'
        try:
            try:
                git(repo, 'worktree', 'add', '--detach', str(tree), product_sha)
            except subprocess.CalledProcessError as exc:
                raise InputError(f'cannot check out {product_sha}: {exc.stderr.decode().strip()}')
            for rel in suite_paths:
                target = tree / rel
                if tree.resolve() not in target.resolve().parents:  # symlink escaping the tree
                    raise InputError(f'suite path resolves outside the worktree: {rel}')
                if target.is_symlink() or target.is_file():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)
            try:
                archive = git(repo, 'archive', suite_sha, '--', *suite_paths).stdout
            except subprocess.CalledProcessError as exc:
                raise InputError(f'cannot read suite paths {suite_paths} at {suite_sha}: {exc.stderr.decode().strip()}')
            subprocess.run(['tar', '-x', '-C', str(tree)], input=archive, check=True)
            proc = subprocess.run(command, shell=True, cwd=tree, capture_output=True, text=True,
                                  env=dict(os.environ, PARITY_RESULTS=str(results)))
            if not results.exists():
                raise InputError(f'spec command wrote no results (exit {proc.returncode}): {proc.stderr[-500:]}')
            try:
                data = json.loads(results.read_text(encoding='utf-8'))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise InputError(f'spec command wrote unreadable results: {exc}')
        finally:
            # Also after a partially failed `worktree add`; a cleanup error never hides the original one.
            subprocess.run(['git', '-C', str(repo), 'worktree', 'remove', '--force', str(tree)], capture_output=True)
            subprocess.run(['git', '-C', str(repo), 'worktree', 'prune'], capture_output=True)
    record = dict(product_sha=product_sha, suite_sha=suite_sha, environment=environment,
                  command=command, exit_code=proc.returncode, results=data)
    check_record(record, 'run')
    return record


def check_record(record, name):
    if not isinstance(record, dict):
        raise InputError(f'{name}: must be an object')
    for key in ('product_sha', 'suite_sha'):
        if not isinstance(record.get(key), str) or not record[key]:
            raise InputError(f'{name}: {key} required')
    if not isinstance(record.get('environment'), dict):
        raise InputError(f'{name}: environment object required')
    results = record.get('results')
    if not isinstance(results, dict) or not results:
        raise InputError(f'{name}: results must record at least one spec')
    for spec, result in results.items():
        if not (isinstance(result, dict) and result.get('outcome') in OUTCOMES
                and isinstance(result.get('observation'), str)):
            raise InputError(f'{name}: {spec}: needs outcome pass|fail and an observation string')


def load_index_rows(index_path):
    """Reuse check_index.py (shipped next to this script) to read the requirement registry."""
    here = Path(__file__).resolve()
    # Installed package: next to this script. Source repository: core/scripts.
    path = next(p for p in (here.with_name('check_index.py'), here.parents[2] / 'core' / 'scripts' / 'check_index.py')
                if p.exists())
    spec = importlib.util.spec_from_file_location('check_index', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        return {r['ID']: r for r in module.parse_index(Path(index_path).read_text(encoding='utf-8'))}
    except (OSError, UnicodeError, ValueError) as exc:
        raise InputError(f'index: {exc}')


def compare(baseline, current, deltas=(), index=None):
    """Return (verdict, reasons). Deltas: [{spec, expected_old, expected_new, obs, ac}]."""
    check_record(baseline, 'baseline')
    check_record(current, 'run')
    if current['suite_sha'] != baseline['suite_sha']:
        return 'FAIL', [f'suite_sha {current["suite_sha"]} is not the frozen suite {baseline["suite_sha"]}']
    if current['environment'] != baseline['environment']:
        return 'UNKNOWN', ['environment differs from the baseline: results are not comparable']
    by_spec = {}
    for delta in deltas:
        if not (isinstance(delta, dict) and isinstance(delta.get('spec'), str) and delta['spec']
                and isinstance(delta.get('obs'), str) and re.fullmatch(r'OBS-\d+', delta['obs'])
                and isinstance(delta.get('ac'), str) and re.fullmatch(r'AC-\d+', delta['ac'])):
            raise InputError('delta needs spec (string), obs (OBS-n), ac (AC-n), expected_old, expected_new')
        for key in ('expected_old', 'expected_new'):
            result = delta.get(key)
            if not (isinstance(result, dict) and result.get('outcome') in OUTCOMES
                    and isinstance(result.get('observation'), str)):
                raise InputError(f'{delta["spec"]}: {key} needs outcome pass|fail and an observation string')
        if delta['spec'] in by_spec:
            raise InputError(f'{delta["spec"]}: more than one delta for the same spec')
        by_spec[delta['spec']] = delta
    failures, unknown = [], []
    for spec, old in sorted(baseline['results'].items()):
        new = current['results'].get(spec)
        if new is None:
            unknown.append(f'{spec}: not run')
            continue
        if new == old:
            continue
        delta = by_spec.get(spec)
        if delta is None:
            failures.append(f'{spec}: changed without an approved delta: {old} -> {new}')
        elif delta['expected_old'] != old or delta['expected_new'] != new:
            failures.append(f'{spec}: change does not match its delta (expected {delta["expected_old"]} -> '
                            f'{delta["expected_new"]}, got {old} -> {new})')
        elif index is None:
            failures.append(f'{spec}: a changed behavior needs INDEX confirmation (--index specs/INDEX.md)')
        else:
            row = index.get(delta['ac'])
            if not row or row['Status'] != 'active' or row['Origin'] != f'deviation:{delta["obs"]}':
                failures.append(f'{spec}: INDEX has no active {delta["ac"]} with origin deviation:{delta["obs"]}')
    extra = sorted(set(current['results']) - set(baseline['results']))
    if extra:
        failures.append(f'specs not in the frozen suite baseline: {", ".join(extra)}')
    if failures:
        return 'FAIL', failures
    if unknown:
        return 'UNKNOWN', unknown
    return 'PASS', []


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f'{path}: {exc}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--repo', default='.')
    r.add_argument('--suite-sha', required=True)
    r.add_argument('--product-sha', required=True)
    r.add_argument('--command', required=True, help='spec command; writes results to $PARITY_RESULTS')
    r.add_argument('--env-file', required=True, help='JSON fingerprint of fixtures/seed/config/runtime')
    r.add_argument('--suite-path', action='append', help='path frozen with the suite (default: specs)')
    r.add_argument('--out', required=True)
    c = sub.add_parser('compare')
    c.add_argument('baseline')
    c.add_argument('run')
    c.add_argument('--deltas', help='JSON list of approved deltas')
    c.add_argument('--index', help='specs/INDEX.md to confirm each delta is an approved deviation')
    args = parser.parse_args(argv)
    try:
        if args.cmd == 'run':
            env = load_json(args.env_file)
            if not isinstance(env, dict):
                raise InputError('env-file must hold a JSON object')
            record = run(args.repo, args.suite_sha, args.product_sha, args.command, env,
                         tuple(args.suite_path or ['specs']))
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(json.dumps(record, indent=2, sort_keys=True))
            print(f'RECORDED: {len(record["results"])} specs, spec command exit {record["exit_code"]}')
            return 0
        deltas = load_json(args.deltas) if args.deltas else []
        if not isinstance(deltas, list):
            raise InputError('deltas must be a JSON list')
        index = load_index_rows(args.index) if args.index else None
        verdict, reasons = compare(load_json(args.baseline), load_json(args.run), deltas, index)
    except InputError as exc:
        print(f'INPUT ERROR: {exc}', file=sys.stderr)
        return 2
    for reason in reasons:
        print(f'{verdict}: {reason}', file=sys.stderr)
    print(f'PARITY {verdict}')
    return 0 if verdict == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
