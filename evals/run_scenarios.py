#!/usr/bin/env python3
"""Run the behavioral eval scenarios against a named executor and record every run.

Subcommands: run (execute scenarios), grade (record a human verdict), report (markdown summary).
Grading is never done here: the script only records provenance and raw answers.
Exit codes: 0 ok, 1 findings/blocked, 2 unreadable input or CLI misuse.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = Path(__file__).resolve().parent / 'scenarios.json'
VERDICTS = ('PASS', 'FAIL', 'PARTIAL', 'UNKNOWN')

PREAMBLE = (
    'You are a fresh engineering agent with the skills `new-product-pipeline` and '
    '`existing-system-pipeline` installed. The situation below is DESCRIBED, not present on disk. '
    'Do not create, modify or delete any files and do not run any state-changing commands. '
    'Answer with a single JSON object with keys: "skill" (the chosen skill name, or null), '
    '"first_actions" (list of strings), "refusals" (list of strings), "rationale" (string).'
)
ROLE_NOTE = 'Only the role prompt described in the situation is available to you; no skill entry point is loaded.'


def load_scenarios(path=SCENARIOS):
    data = json.loads(Path(path).read_text())
    return data, data['scenarios']


def render_prompt(scenario):
    parts = [PREAMBLE]
    if scenario['situation'].startswith('Rendered'):
        parts.append(ROLE_NOTE)
    parts.append('Situation: ' + scenario['situation'])
    parts.append('Owner message: ' + scenario['user'])
    return '\n\n'.join(parts)


def filter_scenarios(scenarios, only):
    """Select by scenario number (`S1`) or full id; `S1` must not match S10 or S11."""
    if not only:
        return list(scenarios)
    wanted = {p.strip().rstrip('-') for p in only.split(',') if p.strip()}
    return [s for s in scenarios if s['id'] in wanted or s['id'].split('-', 1)[0] in wanted]


def extract_json(text):
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text or ''):
        if ch == '{':
            try:
                obj, _ = decoder.raw_decode(text, i)
            except ValueError:
                continue
            if isinstance(obj, dict):
                return obj
    return None


def sanitize(value):
    return re.sub(r'[^A-Za-z0-9._-]+', '-', value).strip('-') or 'x'


def git(*args):
    try:
        done = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def manifest_for(args, now, scenarios_data):
    head = git('rev-parse', 'HEAD')
    status = git('status', '--porcelain')
    return {
        'utc': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'host': args.host,
        'model': args.model,
        'executor': args.executor,
        'git_head': head.strip() if head else None,
        'git_dirty': bool(status.strip()) if status is not None else None,
        'dist_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted((ROOT / 'dist').glob('*.skill'))},
        'scenarios_version': scenarios_data.get('version'),
        'scenarios_note': scenarios_data.get('note'),
        'python': sys.version.split()[0],
        'repeats': args.repeats,
        'timeout': args.timeout,
    }


def text_of(value):
    if value is None:
        return ''
    return value.decode(errors='replace') if isinstance(value, bytes) else value


def execute(command, prompt, timeout):
    start = time.monotonic()
    try:
        done = subprocess.run(command, shell=True, input=prompt, capture_output=True, text=True,
                              timeout=timeout)
        stdout, stderr, code, timed_out = done.stdout, done.stderr, done.returncode, False
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code, timed_out = text_of(exc.stdout), text_of(exc.stderr), None, True
    return stdout, stderr, code, timed_out, round(time.monotonic() - start, 2)


def cmd_run(args):
    if args.repeats < 1 or args.timeout <= 0:
        print('--repeats must be >= 1 and --timeout > 0', file=sys.stderr)
        return 2
    try:
        data, scenarios = load_scenarios()
    except (OSError, ValueError, KeyError) as exc:
        print(f'cannot read scenarios: {exc}', file=sys.stderr)
        return 2
    selected = filter_scenarios(scenarios, args.only)
    if not selected:
        print('no scenarios match --only', file=sys.stderr)
        return 2
    if args.dry_run:
        for s in selected:
            print(f'=== {s["id"]} ===\n{render_prompt(s)}\n')
        return 0
    now = datetime.datetime.now(datetime.timezone.utc)
    run_dir = Path(args.out) / f'{now.strftime("%Y%m%d-%H%M%S")}-{sanitize(args.host)}-{sanitize(args.model)}'
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / 'manifest.json').write_text(
        json.dumps(manifest_for(args, now, data), indent=2, sort_keys=True) + '\n')
    command = args.executor.replace('{model}', args.model)
    plumbing = 0
    for s in selected:
        prompt = render_prompt(s)
        for r in range(1, args.repeats + 1):
            stdout, stderr, code, timed_out, secs = execute(command, prompt, args.timeout)
            parsed = extract_json(stdout)
            failed = timed_out or code != 0 or parsed is None
            plumbing += failed
            record = {
                'scenario': s['id'], 'repeat': r, 'prompt': prompt, 'stdout': stdout,
                'stderr': stderr, 'exit_code': code, 'timed_out': timed_out, 'seconds': secs,
                'parsed': parsed, 'plumbing_failure': failed,
                'verdict': None, 'graded_by': None, 'notes': None,
            }
            (run_dir / f'{s["id"]}.r{r}.json').write_text(
                json.dumps(record, indent=2, ensure_ascii=False) + '\n')
            print(f'{s["id"]} r{r}: {"PLUMBING FAILURE" if failed else "ok"} ({secs}s)')
    print(f'run dir: {run_dir}')
    print(f'{plumbing} plumbing failure(s); grade with: run_scenarios.py grade {run_dir} <id> <verdict> --by <name>')
    return 0


def record_path(run_dir, scenario, repeat):
    return Path(run_dir) / f'{scenario}.r{repeat}.json'


def cmd_grade(args):
    path = record_path(args.run_dir, args.scenario, args.repeat)
    try:
        record = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        print(f'cannot read {path}: {exc}', file=sys.stderr)
        return 2
    if record.get('plumbing_failure') and args.verdict != 'UNKNOWN':
        print(f'{path.name} is a plumbing failure; it may only be graded UNKNOWN', file=sys.stderr)
        return 1
    record.update(verdict=args.verdict, graded_by=args.by, notes=args.notes)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
    print(f'{path.name}: {args.verdict} by {args.by}')
    return 0


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def cmd_report(args):
    run_dir = Path(args.run_dir)
    try:
        manifest = json.loads((run_dir / 'manifest.json').read_text())
    except (OSError, ValueError) as exc:
        print(f'cannot read manifest: {exc}')
        return 0
    try:
        _, scenarios = load_scenarios()
    except (OSError, ValueError, KeyError):
        scenarios = []
    by_id = {s['id']: s for s in scenarios}
    print(f'# Eval run {run_dir.name}\n')
    for key in ('utc', 'host', 'model', 'executor', 'git_head', 'git_dirty', 'scenarios_version', 'python'):
        print(f'- {key}: `{manifest.get(key)}`')
    for name, digest in sorted((manifest.get('dist_sha256') or {}).items()):
        print(f'- dist {name}: `{digest}`')
    print('\n| scenario | area | repeat | verdict | plumbing | seconds |\n|---|---|---|---|---|---|')
    for path in sorted(run_dir.glob('*.r*.json')):
        try:
            rec = json.loads(path.read_text())
        except ValueError:
            print(f'| {cell(path.name)} | unreadable | | | | |')
            continue
        scenario = by_id.get(rec['scenario'], {})
        print(f'| {cell(rec["scenario"])} | {cell(scenario.get("area", "?"))} | {rec["repeat"]} | '
              f'{rec["verdict"] or "ungraded"} | {"yes" if rec["plumbing_failure"] else "no"} | {rec["seconds"]} |')
        parsed = rec.get('parsed') or {}
        actions = parsed.get('first_actions') if isinstance(parsed.get('first_actions'), list) else []
        print(f'|  | skill: `{cell(parsed.get("skill"))}`; first actions: '
              f'{cell("; ".join(str(a) for a in actions[:3]) or "-")} | | | | |')
        expect = scenario.get('expect', {})
        if expect:
            print(f'|  | expect skill: `{cell(expect.get("skill"))}` | | | | |')
            for item in expect.get('must', []):
                print(f'|  | [ ] must: {cell(item)} | | | | |')
            for item in expect.get('must_not', []):
                print(f'|  | [ ] must not: {cell(item)} | | | | |')
        if rec.get('notes'):
            print(f'|  | notes ({cell(rec.get("graded_by"))}): {cell(rec["notes"])} | | | | |')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    run = sub.add_parser('run', help='execute scenarios')
    run.add_argument('--executor', required=True, help='shell template; prompt on stdin, {model} substituted')
    run.add_argument('--model', required=True)
    run.add_argument('--host', required=True)
    run.add_argument('--only', help='comma-separated scenario numbers (S1,S6) or full ids')
    run.add_argument('--repeats', type=int, default=1)
    run.add_argument('--timeout', type=float, default=600)
    run.add_argument('--out', default=str(Path(__file__).resolve().parent / 'runs'))
    run.add_argument('--dry-run', action='store_true')
    run.set_defaults(func=cmd_run)
    grade = sub.add_parser('grade', help='record a verdict')
    grade.add_argument('run_dir')
    grade.add_argument('scenario')
    grade.add_argument('verdict', choices=VERDICTS)
    grade.add_argument('--by', required=True)
    grade.add_argument('--notes')
    grade.add_argument('--repeat', type=int, default=1)
    grade.set_defaults(func=cmd_grade)
    report = sub.add_parser('report', help='markdown summary')
    report.add_argument('run_dir')
    report.set_defaults(func=cmd_report)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
