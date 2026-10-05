"""Phase-2 contract: CI/local evidence, slice vs initiative, two-pass QA coverage, CI artifact, release."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'validate_gate.py'
spec = importlib.util.spec_from_file_location('validate_gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

SHA = 'c0ffee1'
CI = dict(provider='github-actions', repository='owner/repo', workflow='.github/workflows/ci.yml',
          job='test', run_id='123', run_attempt=1, head_sha=SHA, conclusion='success', url='https://ci/123')


def command(gid='tests', runner='ci', **extra):
    record = dict(id=gid, kind='command', snapshot=SHA, status='PASS', evidence='log',
                  command='pytest -q', exit_code=0, failures=[], runner=runner)
    if runner == 'ci':
        record['ci'] = dict(CI)
    else:
        record['local'] = dict(command='make ci', worktree='clean', head_sha=SHA, reason='push not authorized')
    record.update(extra)
    return record


def review(gid, **extra):
    return dict(dict(id=gid, kind='review', snapshot=SHA, status='PASS', evidence='report',
                     rubric_version='qa-v2', findings=[]), **extra)


def slice_receipt(*gates):
    gates = list(gates) or [command()]
    return dict(schema_version=2, phase='3.1', snapshot=SHA, snapshot_kind='commit', scope='slice',
                strict_mode=True, required_gates=[g['id'] for g in gates], gates=gates)


def initiative_receipt():
    r = slice_receipt(command(), command(gate.INDEX_GATE, command='check_index.py'),
                      review(gate.QA_BLIND, coverage=['AC-001', 'AC-002']),
                      review(gate.QA_INTERNAL, coverage=['QR-001']))
    r.update(scope='initiative', active_criteria=['AC-001', 'AC-002', 'QR-001'])
    return r


class Blocked(unittest.TestCase):
    def assertBlocked(self, fn, *args, contains=''):
        with self.assertRaises(ValueError) as ctx:
            fn(*args)
        self.assertIn(contains, str(ctx.exception))


class RunnerTests(Blocked):
    def test_ci_on_exact_commit_passes(self):
        self.assertEqual(gate.validate(slice_receipt()), [])

    def test_ci_on_other_commit_fails(self):
        r = slice_receipt(); r['gates'][0]['ci']['head_sha'] = 'other'
        self.assertBlocked(gate.validate, r, contains='different commit')

    def test_ci_on_manifest_snapshot_fails(self):
        r = slice_receipt(); r['snapshot_kind'] = 'manifest'
        self.assertBlocked(gate.validate, r, contains='commit snapshot')

    def test_local_on_manifest_passes_with_base_head(self):
        r = slice_receipt(command(runner='local')); r['snapshot_kind'] = 'manifest'
        r['gates'][0]['local']['head_sha'] = 'base-head'
        self.assertEqual(gate.validate(r), [])

    def test_local_needs_clean_worktree_and_reason(self):
        for key, val in (('worktree', 'dirty'), ('reason', '')):
            r = slice_receipt(command(runner='local')); r['gates'][0]['local'][key] = val
            self.assertBlocked(gate.validate, r)

    def test_local_rejected_when_plan_requires_ci(self):
        r = slice_receipt(command(runner='local')); r['require_ci'] = True
        self.assertBlocked(gate.validate, r, contains='requires CI')

    def test_ci_failure_conclusion_is_fail_not_pass(self):
        r = slice_receipt(); r['gates'][0]['ci']['conclusion'] = 'failure'
        self.assertBlocked(gate.validate, r, contains='conclusion disagrees')

    def test_legacy_exception_through_ci_keeps_nonzero_exit(self):
        r = slice_receipt(command(status='FAIL', exit_code=1, failures=['t_old::E'], baseline_exception=dict(
            baseline_snapshot='base', scope='legacy', approval='owner', evidence='log', test_only=True,
            failures=['t_old::E'])))
        r['gates'][0]['ci']['conclusion'] = 'failure'
        self.assertEqual(gate.validate(r), ['tests'])
        r['gates'][0]['ci']['conclusion'] = 'success'
        self.assertBlocked(gate.validate, r)

    def test_missing_runner_or_attempt_rejected(self):
        r = slice_receipt(); del r['gates'][0]['runner']; self.assertBlocked(gate.validate, r)
        r = slice_receipt(); r['gates'][0]['ci']['run_attempt'] = 0; self.assertBlocked(gate.validate, r)

    def test_receipt_v1_rejected(self):
        r = slice_receipt(); r['schema_version'] = 1
        self.assertBlocked(gate.validate, r, contains='accepts 2 only')


class ScopeAndQATests(Blocked):
    def test_slice_done_without_final_qa(self):
        self.assertEqual(gate.validate(slice_receipt()), [])

    def test_initiative_complete_with_both_qa_passes(self):
        self.assertEqual(gate.validate(initiative_receipt()), [])

    def test_initiative_without_final_qa_fails(self):
        r = initiative_receipt()
        r['gates'] = [g for g in r['gates'] if g['id'] != gate.QA_BLIND]
        r['required_gates'].remove(gate.QA_BLIND)
        self.assertBlocked(gate.validate, r, contains=gate.QA_BLIND)

    def test_incomplete_coverage_is_unknown(self):
        r = initiative_receipt(); r['gates'][2]['coverage'] = ['AC-001']
        self.assertBlocked(gate.validate, r, contains='UNKNOWN, incomplete coverage: AC-002')
        r = initiative_receipt(); r['gates'][3]['coverage'] = []
        self.assertBlocked(gate.validate, r, contains='QR-001')

    def test_mixed_snapshots_after_repair_fail(self):
        r = initiative_receipt(); r['gates'][3]['snapshot'] = 'before-repair'
        self.assertBlocked(gate.validate, r, contains='stale snapshot')

    def test_initiative_needs_commit_snapshot(self):
        r = initiative_receipt(); r['snapshot_kind'] = 'manifest'
        self.assertBlocked(gate.validate, r)


class CIArtifactTests(Blocked):
    def artifact(self, **over):
        a = dict(repository='owner/repo', workflow='.github/workflows/ci.yml', job='test', run_id='123',
                 run_attempt=1, head_sha=SHA,
                 commands=[dict(command='pytest -q', exit_code=0, failures=[])])
        a.update(over)
        return a

    def test_matching_artifact_passes(self):
        gate.validate_ci_artifact(slice_receipt(), self.artifact())

    def test_declared_command_missing_from_artifact_fails(self):
        self.assertBlocked(gate.validate_ci_artifact, slice_receipt(), self.artifact(commands=[]),
                           contains='not executed')

    def test_skipped_command_fails(self):
        a = self.artifact(); a['commands'][0]['skipped'] = True
        self.assertBlocked(gate.validate_ci_artifact, slice_receipt(), a, contains='skipped')

    def test_other_attempt_fails(self):
        self.assertBlocked(gate.validate_ci_artifact, slice_receipt(), self.artifact(run_attempt=2),
                           contains='run_attempt')

    def test_exit_code_mismatch_fails(self):
        a = self.artifact(); a['commands'][0]['exit_code'] = 1
        self.assertBlocked(gate.validate_ci_artifact, slice_receipt(), a, contains='exit code')


class ProbeRegressionTests(Blocked):
    """Inputs from the PR #18 review probes."""

    def test_artifact_type_confusion_rejected(self):
        a = CIArtifactTests().artifact
        for bad, needle in ((a(run_attempt=True), 'run_attempt'), (a(run_attempt=1.0), 'run_attempt')):
            self.assertBlocked(gate.validate_ci_artifact, slice_receipt(), bad, contains=needle)
        for field, value in (('exit_code', False), ('exit_code', 0.0), ('failures', False), ('failures', 123),
                             ('failures', [1, 'x']), ('skipped', 1), ('skipped', 'true')):
            art = a(); art['commands'][0][field] = value
            with self.subTest(field=field, value=value):
                self.assertBlocked(gate.validate_ci_artifact, slice_receipt(), art)
        art = a(); del art['commands'][0]['failures']
        self.assertBlocked(gate.validate_ci_artifact, slice_receipt(), art, contains='failures')

    def test_criterion_with_trailing_newline_rejected(self):
        r = initiative_receipt(); r['active_criteria'].append('AC-003\n')
        self.assertBlocked(gate.validate, r)

    def test_smoke_for_inactive_criterion_rejected(self):
        rel = ReleaseTests().release(); rel['smoke'][0]['criterion'] = 'AC-999'
        self.assertBlocked(gate.validate_release, rel, initiative_receipt(), contains='not an active criterion')

    def test_index_gate_must_be_a_passing_command(self):
        r = initiative_receipt()
        r['gates'] = [g for g in r['gates'] if g['id'] != gate.INDEX_GATE] + [review(gate.INDEX_GATE)]
        self.assertBlocked(gate.validate_release, ReleaseTests().release(), r, contains='passing index-check command')

    def test_release_without_receipt_hash_rejected(self):
        rel = ReleaseTests().release(); del rel['receipt_sha256']
        self.assertBlocked(gate.validate_release, rel, initiative_receipt(), contains='receipt_sha256')


class ReleaseTests(Blocked):
    def release(self, **over):
        r = dict(done_snapshot=SHA, deployed_sha=SHA, environment='prod', authorization='owner request 2026-10-05',
                 receipt='SPEC_PLAN/gates/final.json', receipt_sha256='checked-by-cli', first_release=True,
                 smoke=[dict(id='login', criterion='AC-001', status='PASS', evidence='smoke.log')])
        r.update(over)
        return r

    def test_release_accepted(self):
        gate.validate_release(self.release(), initiative_receipt())

    def test_deployed_other_commit_fails(self):
        self.assertBlocked(gate.validate_release, self.release(deployed_sha='other'), initiative_receipt(),
                           contains='not the accepted one')

    def test_smoke_not_pass_fails(self):
        for status in ('UNKNOWN', 'FAIL', None):
            rel = self.release(); rel['smoke'][0]['status'] = status
            self.assertBlocked(gate.validate_release, rel, initiative_receipt(), contains='smoke not PASS')

    def test_generic_or_empty_smoke_fails(self):
        self.assertBlocked(gate.validate_release, self.release(smoke=[]), initiative_receipt())
        rel = self.release(); rel['smoke'][0]['criterion'] = 'health'
        self.assertBlocked(gate.validate_release, rel, initiative_receipt(), contains='AC/QR')

    def test_slice_receipt_cannot_release(self):
        self.assertBlocked(gate.validate_release, self.release(), slice_receipt(), contains='initiative')

    def test_receipt_for_other_snapshot_fails(self):
        self.assertBlocked(gate.validate_release, self.release(done_snapshot='zzz', deployed_sha='zzz'),
                           initiative_receipt(), contains='different snapshot')

    def test_first_release_without_index_in_accepted_receipt_fails(self):
        r = initiative_receipt()
        r['gates'] = [g for g in r['gates'] if g['id'] != gate.INDEX_GATE]
        r['required_gates'].remove(gate.INDEX_GATE)
        self.assertBlocked(gate.validate_release, self.release(), r, contains='INDEX before final QA')
        gate.validate_release(self.release(first_release=False), r)


class DocumentationTests(unittest.TestCase):
    def test_gate_policy_example_receipt_is_valid(self):
        policy = (Path(__file__).resolve().parents[1] / 'references' / 'gate-policy.md').read_text()
        block = policy.split('## Receipt (minimal complete example)', 1)[1].split('```json', 1)[1].split('```', 1)[0]
        self.assertEqual(gate.validate(json.loads(block)), [])


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)

    def test_release_and_artifact_flags(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            body = json.dumps(initiative_receipt())
            (d / 'r.json').write_text(body)
            rel = ReleaseTests().release(receipt_sha256=hashlib.sha256(body.encode()).hexdigest())
            (d / 'rel.json').write_text(json.dumps(rel))
            full = CIArtifactTests().artifact()
            full['commands'].append(dict(command='check_index.py', exit_code=0, failures=[]))
            (d / 'a.json').write_text(json.dumps(full))
            ok = self.run_cli('--ci-artifact', d / 'a.json', '--release', d / 'rel.json', d / 'r.json')
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertIn('RELEASED', ok.stdout)
            bad = copy.deepcopy(CIArtifactTests().artifact(run_attempt=2))
            (d / 'a.json').write_text(json.dumps(bad))
            self.assertEqual(self.run_cli('--ci-artifact', d / 'a.json', d / 'r.json').returncode, 1)
            # release bound to another receipt (hash mismatch)
            (d / 'rel.json').write_text(json.dumps(dict(rel, receipt_sha256='0' * 64)))
            self.assertEqual(self.run_cli('--release', d / 'rel.json', d / 'r.json').returncode, 1)
            # malformed artifact is an input error, not a traceback
            (d / 'a.json').write_text(json.dumps(CIArtifactTests().artifact(commands=[dict(
                command='pytest -q', exit_code=0, failures=123)])))
            bad = self.run_cli('--ci-artifact', d / 'a.json', d / 'r.json')
            self.assertIn(bad.returncode, (1, 2)); self.assertNotIn('Traceback', bad.stderr)


if __name__ == '__main__':
    unittest.main()
