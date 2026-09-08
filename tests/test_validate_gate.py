import copy
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


def receipt():
    return dict(schema_version=1, phase='3.1', snapshot='sha-a', strict_mode=True,
                required_gates=['tests', 'review', 'owner'], gates=[
                    dict(id='tests', kind='command', snapshot='sha-a', status='PASS',
                         evidence='test log', command='pytest', exit_code=0, failures=[]),
                    dict(id='review', kind='review', snapshot='sha-a', status='PASS',
                         evidence='diff review', rubric_version='solid-v2', findings=[]),
                    dict(id='owner', kind='approval', snapshot='sha-a', status='PASS',
                         evidence='explicit request', decision='approved')])


def finding(status='FAIL', severity='blocking'):
    return dict(criterion='AC-001', status=status, severity=severity,
                evidence='observed result / missing evidence', fix='bounded correction or check')


class CompletionTests(unittest.TestCase):
    def assertBlocked(self, r):
        with self.assertRaises(ValueError):
            gate.validate(r)

    def test_complete_receipt(self):
        self.assertEqual(gate.validate(receipt()), [])

    def test_self_review_alone_cannot_complete(self):
        r = receipt(); r['gates'] = r['gates'][:1]; self.assertBlocked(r)

    def test_missing_owner_approval(self):
        r = receipt(); r['gates'][2]['decision'] = 'unapproved'; self.assertBlocked(r)

    def test_reused_approval_requires_evidence(self):
        r = receipt(); r['gates'][2]['decision'] = 'reused'; gate.validate(r)
        r['gates'][2]['evidence'] = ''; self.assertBlocked(r)

    def test_changed_snapshot_invalidates_review(self):
        r = receipt(); r['gates'][1]['snapshot'] = 'old'; self.assertBlocked(r)

    def test_missing_gate_set_is_not_success(self):
        r = receipt(); r['required_gates'] = []; r['gates'] = []; self.assertBlocked(r)

    def test_duplicate_or_extra_gates(self):
        for change in ('duplicate', 'extra', 'required_duplicate'):
            with self.subTest(change=change):
                r = receipt()
                if change == 'duplicate': r['gates'].append(copy.deepcopy(r['gates'][0]))
                elif change == 'extra': r['gates'].append(dict(r['gates'][0], id='unplanned'))
                else: r['required_gates'].append('tests')
                self.assertBlocked(r)

    def test_critical_fail_blocks_both_modes(self):
        for strict in (True, False):
            r = receipt(); r['strict_mode'] = strict
            r['gates'][1].update(status='FAIL', findings=[finding()]); self.assertBlocked(r)

    def test_major_fail_advisory_only_when_not_strict(self):
        r = receipt(); r['gates'][1].update(status='FAIL', findings=[finding(severity='major')])
        self.assertBlocked(r)
        r['strict_mode'] = False; r['gates'][1]['status'] = 'PASS'; gate.validate(r)

    def test_minor_failure_is_reported_but_advisory(self):
        r = receipt(); r['gates'][1]['findings'] = [finding(severity='minor')]; gate.validate(r)

    def test_unknown_blocks_even_when_not_strict(self):
        r = receipt(); r['strict_mode'] = False
        r['gates'][1].update(status='UNKNOWN', findings=[finding('UNKNOWN', 'minor')]); self.assertBlocked(r)

    def test_false_pass_and_missing_evidence_are_rejected(self):
        r = receipt(); r['gates'][1]['findings'] = [finding()]; self.assertBlocked(r)
        r = receipt(); r['gates'][1]['evidence'] = ''; self.assertBlocked(r)

    def test_unrun_check_or_nonzero_cannot_pass(self):
        for code in (None, 1, True):
            r = receipt(); r['gates'][0]['exit_code'] = code; self.assertBlocked(r)

    def test_schema_is_strict_about_types_and_status(self):
        for key, val in [('schema_version', True), ('strict_mode', 'false'), ('snapshot', ''), ('gates', {})]:
            r = receipt(); r[key] = val; self.assertBlocked(r)
        for kind in ('unknown', None):
            r = receipt(); r['gates'][0]['kind'] = kind; self.assertBlocked(r)

    def legacy(self):
        r = receipt(); r['gates'][0].update(status='FAIL', exit_code=1,
            failures=['test_old::AssertionError expected 2'], baseline_exception=dict(
                baseline_snapshot='baseline', scope='legacy tests only', approval='owner approval before gate',
                evidence='baseline log and matching environment', test_only=True,
                failures=['test_old::AssertionError expected 2', 'test_fixed::Timeout']))
        return r

    def test_exact_agreed_baseline_subset_can_complete_with_warning(self):
        self.assertEqual(gate.validate(self.legacy()), ['tests'])

    def test_same_failure_count_does_not_hide_new_regression(self):
        r = self.legacy(); r['gates'][0]['failures'] = ['test_new::AssertionError']; self.assertBlocked(r)

    def test_changed_failure_signature_is_regression(self):
        r = self.legacy(); r['gates'][0]['failures'] = ['test_old::Timeout']; self.assertBlocked(r)

    def test_waiver_needs_test_scope_approval_and_execution(self):
        for key, val in [('test_only', False), ('approval', ''), ('failures', []), ('baseline_snapshot', '')]:
            r = self.legacy(); r['gates'][0]['baseline_exception'][key] = val; self.assertBlocked(r)
        r = self.legacy(); r['gates'][0]['exit_code'] = None; self.assertBlocked(r)

    def test_interrupted_process_cannot_use_legacy_exception(self):
        r = self.legacy(); r['gates'][0]['exit_code'] = -9; self.assertBlocked(r)

    def test_waiver_cannot_bypass_review(self):
        r = receipt(); r['gates'][1]['baseline_exception'] = self.legacy()['gates'][0]['baseline_exception']
        self.assertBlocked(r)

    def test_unresolved_prompt(self):
        self.assertEqual(gate.unresolved('phase {{CURRENT_PHASE}} / {{ TECH_STACK }}'), ['CURRENT_PHASE', 'TECH_STACK'])
        self.assertEqual(gate.unresolved('Implement phase 3.1'), [])

    def test_cli_does_not_modify_input(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'receipt.json'; body = json.dumps(receipt()); path.write_text(body)
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr); self.assertEqual(path.read_text(), body)
            path.write_text('{broken')
            self.assertEqual(subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
