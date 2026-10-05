#!/usr/bin/env python3
"""Validate declared phase evidence; does not execute checks or authorize actions.

Checks consistency of the supplied records only (schema v2): it cannot prove that a CI run,
an approval or a smoke check really happened. The coordinator verifies provenance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = 2
QA_BLIND, QA_INTERNAL, INDEX_GATE = 'qa-blind', 'qa-internal', 'index-check'
CI_FIELDS = ('provider', 'repository', 'workflow', 'job', 'run_id', 'head_sha', 'conclusion', 'url')
CRITERION = re.compile(r'(AC|QR)-\d+')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and all(text(item) for item in value)


def unresolved(prompt):
    return sorted(set(re.findall(r'\{\{\s*([^{}]+?)\s*\}\}', prompt)))


def validate_runner(name, record, receipt):
    """Bind a command record to where it ran: CI on the exact commit, or a clean local run."""
    runner = record.get('runner')
    require(runner in ('ci', 'local'), f'{name}: runner must be ci or local')
    if runner == 'ci':
        ci = record.get('ci')
        require(isinstance(ci, dict), f'{name}: ci record required')
        for field in CI_FIELDS:
            require(text(ci.get(field)), f'{name}: ci.{field} required')
        require(type(ci.get('run_attempt')) is int and ci['run_attempt'] >= 1,
                f'{name}: ci.run_attempt must be a positive integer')
        require(receipt['snapshot_kind'] == 'commit', f'{name}: CI evidence needs a commit snapshot')
        require(ci['head_sha'] == receipt['snapshot'], f'{name}: CI ran on a different commit')
        require((ci['conclusion'] == 'success') == (record['exit_code'] == 0),
                f'{name}: CI conclusion disagrees with exit code')
    else:
        require(not receipt.get('require_ci'), f'{name}: plan requires CI evidence, got local')
        local = record.get('local')
        require(isinstance(local, dict), f'{name}: local record required')
        require(local.get('worktree') == 'clean', f'{name}: local run must use a clean worktree')
        require(text(local.get('head_sha')) and text(local.get('reason')),
                f'{name}: local run needs base head_sha and a reason')
        if receipt['snapshot_kind'] == 'commit':
            require(local['head_sha'] == receipt['snapshot'], f'{name}: local run on a different commit')


def validate_command(name, record, receipt, exceptions):
    require(text(record.get('command')), f'{name}: command required')
    code, failures = record.get('exit_code'), record.get('failures')
    require(type(code) is int, f'{name}: check was not executed or exit code invalid')
    require(strings(failures), f'{name}: failures must list test identities and signatures')
    require(record['status'] == ('PASS' if code == 0 else 'FAIL'), f'{name}: status disagrees with exit code')
    validate_runner(name, record, receipt)
    if code == 0:
        require(not failures and 'baseline_exception' not in record,
                f'{name}: successful command cannot have failures/exception')
        return
    require(code > 0, f'{name}: interrupted process cannot use a baseline exception')
    waiver = record.get('baseline_exception')
    require(isinstance(waiver, dict), f'{name}: failed command without approved exception')
    require(waiver.get('test_only') is True, f'{name}: exception restricted to legacy tests')
    for field in ('baseline_snapshot', 'scope', 'approval', 'evidence'):
        require(text(waiver.get(field)), f'{name}: exception missing {field}')
    baseline = waiver.get('failures')
    require(strings(baseline) and baseline and failures, f'{name}: empty baseline/current failures')
    require(set(failures) <= set(baseline), f'{name}: new test identity or failure signature')
    exceptions.append(name)


def validate_review(name, record, receipt):
    require(text(record.get('rubric_version')), f'{name}: rubric_version required')
    findings = record.get('findings')
    require(isinstance(findings, list), f'{name}: findings list required')
    blocked, unknown = False, False
    for finding in findings:
        require(isinstance(finding, dict), f'{name}: invalid finding')
        for field in ('criterion', 'evidence', 'fix'):
            require(text(finding.get(field)), f'{name}: finding missing {field}')
        fs, severity = finding.get('status'), finding.get('severity')
        require(fs in ('FAIL', 'UNKNOWN'), f'{name}: invalid finding status')
        require(severity in ('blocking', 'major', 'minor'), f'{name}: invalid severity')
        blocked |= fs == 'FAIL' and (severity == 'blocking' or
                                    (severity == 'major' and receipt['strict_mode']))
        unknown |= fs == 'UNKNOWN'
    expected = 'FAIL' if blocked else 'UNKNOWN' if unknown else 'PASS'
    require(record['status'] == expected, f'{name}: verdict disagrees with findings')
    require(record['status'] == 'PASS', f'{name}: unresolved review ({record["status"]})')


def validate_initiative(receipt, records):
    """Initiative completion = final two-pass QA on a commit covering every active criterion."""
    require(receipt['snapshot_kind'] == 'commit', 'initiative completion needs a commit snapshot')
    for qa in (QA_BLIND, QA_INTERNAL):
        require(qa in records and records[qa]['kind'] == 'review',
                f'initiative completion requires the {qa} review gate')
    active = receipt.get('active_criteria')
    require(strings(active) and active and all(CRITERION.fullmatch(c) for c in active),
            'active_criteria must list AC-/QR- IDs')
    for qa, prefix in ((QA_BLIND, 'AC-'), (QA_INTERNAL, 'QR-')):
        coverage = records[qa].get('coverage')
        require(strings(coverage), f'{qa}: coverage list required')
        missing = sorted(c for c in active if c.startswith(prefix) and c not in coverage)
        require(not missing, f'{qa}: UNKNOWN, incomplete coverage: {", ".join(missing)}')


def validate(receipt):
    require(isinstance(receipt, dict), 'receipt must be an object')
    require(type(receipt.get('schema_version')) is int and receipt['schema_version'] == SCHEMA,
            'unsupported schema_version (this validator accepts 2 only)')
    require(text(receipt.get('phase')) and text(receipt.get('snapshot')), 'phase and snapshot required')
    require(receipt.get('snapshot_kind') in ('commit', 'manifest'), 'snapshot_kind must be commit or manifest')
    require(receipt.get('scope') in ('slice', 'initiative'), 'scope must be slice or initiative')
    require(type(receipt.get('strict_mode')) is bool, 'strict_mode must be boolean')
    require(type(receipt.get('require_ci', False)) is bool, 'require_ci must be boolean')
    required = receipt.get('required_gates')
    require(strings(required) and required, 'required_gates must be a nonempty string list')
    require(len(set(required)) == len(required), 'duplicate required gates')
    gates = receipt.get('gates')
    require(isinstance(gates, list), 'gates must be a list')
    records, exceptions = {}, []
    for record in gates:
        require(isinstance(record, dict), 'gate must be an object')
        name = record.get('id')
        require(text(name), 'gate id required')
        require(name not in records, f'{name}: duplicate gate')
        records[name] = record
        require(record.get('snapshot') == receipt['snapshot'], f'{name}: stale snapshot')
        require(text(record.get('evidence')), f'{name}: evidence required')
        require(record.get('status') in ('PASS', 'FAIL', 'UNKNOWN'), f'{name}: invalid status')
        kind = record.get('kind')
        require(kind in ('command', 'review', 'approval'), f'{name}: invalid kind')
        require(kind == 'command' or 'baseline_exception' not in record,
                f'{name}: only test commands may have baseline exceptions')
        if kind == 'command':
            validate_command(name, record, receipt, exceptions)
        elif kind == 'approval':
            require(record['status'] == 'PASS' and record.get('decision') in ('approved', 'reused'),
                    f'{name}: missing approval')
        else:
            validate_review(name, record, receipt)
    require(set(records) == set(required), 'gate set differs from required_gates')
    if receipt['scope'] == 'initiative':
        validate_initiative(receipt, records)
    return exceptions


def validate_ci_artifact(receipt, artifact):
    """Cross-check CI command records against the command-level artifact the CI job published."""
    require(isinstance(artifact, dict) and isinstance(artifact.get('commands'), list),
            'ci artifact must be an object with a commands list')
    run = {k: artifact.get(k) for k in ('repository', 'workflow', 'job', 'run_id', 'run_attempt', 'head_sha')}
    require(all(text(run[k]) for k in ('repository', 'workflow', 'job', 'run_id', 'head_sha')),
            'ci artifact: repository/workflow/job/run_id/head_sha must be strings')
    require(type(run['run_attempt']) is int, 'ci artifact: run_attempt must be an integer')
    for record in receipt['gates']:
        if record.get('kind') != 'command' or record.get('runner') != 'ci':
            continue
        name, ci = record['id'], record['ci']
        for key, value in run.items():
            require(type(ci.get(key)) is type(value) and ci.get(key) == value,
                    f'{name}: ci.{key} differs from the CI artifact')
        matches = [c for c in artifact['commands'] if isinstance(c, dict) and c.get('command') == record['command']]
        require(matches, f'{name}: command not found in the CI artifact (not executed by that run)')
        entry = matches[-1]
        require(type(entry.get('skipped', False)) is bool, f'{name}: artifact skipped must be boolean')
        require(not entry.get('skipped', False), f'{name}: command was skipped in CI')
        require(type(entry.get('exit_code')) is int, f'{name}: artifact exit_code must be an integer')
        require(entry['exit_code'] == record['exit_code'], f'{name}: exit code differs from the CI artifact')
        require(isinstance(entry.get('failures'), list) and all(isinstance(f, str) for f in entry['failures']),
                f'{name}: artifact failures must be a list of strings')
        require(sorted(entry['failures']) == sorted(record['failures']),
                f'{name}: failures differ from the CI artifact')


def validate_release(release, receipt, receipt_bytes=None):
    """Released = the accepted initiative commit is what was deployed and every smoke check passed."""
    require(isinstance(release, dict), 'release must be an object')
    for field in ('done_snapshot', 'deployed_sha', 'environment', 'authorization', 'receipt', 'receipt_sha256'):
        require(text(release.get(field)), f'release: {field} required')
    if receipt_bytes is not None:
        require(hashlib.sha256(receipt_bytes).hexdigest() == release['receipt_sha256'],
                'release: receipt_sha256 does not match the supplied receipt')
    require(type(release.get('first_release')) is bool, 'release: first_release must be boolean')
    validate(receipt)
    require(receipt['scope'] == 'initiative', 'release: receipt must be an initiative completion')
    require(receipt['snapshot'] == release['done_snapshot'], 'release: receipt is for a different snapshot')
    require(release['deployed_sha'] == release['done_snapshot'], 'release: deployed commit is not the accepted one')
    if release['first_release']:
        index = next((g for g in receipt['gates'] if g['id'] == INDEX_GATE), None)
        require(index is not None and index['kind'] == 'command' and index['status'] == 'PASS',
                f'release: first release needs a passing {INDEX_GATE} command in the accepted receipt '
                f'(INDEX before final QA)')
    smoke = release.get('smoke')
    require(isinstance(smoke, list) and smoke, 'release: approved smoke checks required')
    for check in smoke:
        require(isinstance(check, dict) and text(check.get('id')) and text(check.get('evidence')),
                'release: smoke check needs id and evidence')
        require(isinstance(check.get('criterion'), str) and CRITERION.fullmatch(check['criterion']),
                f'{check.get("id")}: smoke must name an AC/QR')
        require(check['criterion'] in receipt['active_criteria'],
                f'{check["id"]}: smoke criterion {check["criterion"]} is not an active criterion of the receipt')
        require(check.get('status') == 'PASS', f'{check["id"]}: smoke not PASS ({check.get("status")})')


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompt', action='store_true', help='check rendered brief for unresolved tokens')
    parser.add_argument('--ci-artifact', type=Path, help='cross-check CI records against this artifact')
    parser.add_argument('--release', type=Path, help='validate a release record against the receipt')
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    try:
        content = args.path.read_text(encoding='utf-8')
        if args.prompt:
            remaining = unresolved(content)
            require(not remaining, 'unresolved placeholders: ' + ', '.join(remaining))
            print('PASS: no unresolved template tokens')
            return 0
        try:
            receipt = json.loads(content)
            artifact = load_json(args.ci_artifact) if args.ci_artifact else None
            release = load_json(args.release) if args.release else None
        except json.JSONDecodeError as exc:
            print(f'INPUT ERROR: {exc}', file=sys.stderr)
            return 2
        exceptions = validate(receipt)
        if artifact is not None:
            validate_ci_artifact(receipt, artifact)
        if release is not None:
            validate_release(release, receipt, content.encode('utf-8'))
            print('RELEASED: release record accepted')
            return 0
        suffix = '; agreed baseline exceptions: ' + ', '.join(exceptions) if exceptions else ''
        print('ELIGIBLE: declared gate receipt accepted' + suffix)
        return 0
    except (OSError, UnicodeError) as exc:
        print(f'INPUT ERROR: {exc}', file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        return 1
    except (TypeError, KeyError, AttributeError) as exc:
        print(f'INPUT ERROR: malformed record ({type(exc).__name__}: {exc})', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
