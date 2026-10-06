import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'quality_ratchet.py'
spec = importlib.util.spec_from_file_location('quality_ratchet', SCRIPT)
qr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qr)

CC = {'cyclomatic': 10}  # profile reduced to one metric for focused cases


def snap(tool='lizard 1.17.10', **units):
    return dict(tool=tool, units=units)


def full(c=5, g=5, crap=3):
    return dict(cyclomatic=c, cognitive=g, crap=crap)


class RatchetTests(unittest.TestCase):
    def test_existing_unit_improving_above_limit_passes(self):
        self.assertEqual(qr.compare(snap(f=dict(cyclomatic=20)), snap(f=dict(cyclomatic=18)), CC), [])

    def test_existing_unit_worsening_fails(self):
        errors = qr.compare(snap(f=dict(cyclomatic=18)), snap(f=dict(cyclomatic=19)), CC)
        self.assertIn('worsened 18 -> 19', errors[0])

    def test_new_unit_over_absolute_limit_fails(self):
        self.assertIn('new unit cyclomatic 12 > limit 10', qr.compare(snap(), snap(g=dict(cyclomatic=12)), CC)[0])

    def test_new_unit_within_full_profile_passes(self):
        self.assertEqual(qr.compare(snap(), snap(g=full(10, 15, 4))), [])

    def test_tool_version_change_without_new_baseline_fails(self):
        errors = qr.compare(snap(f=full()), snap('lizard 1.18.0', f=full()))
        self.assertIn('commit a new baseline', errors[0])

    def test_average_crap_ratchet(self):
        self.assertTrue(qr.compare(snap(a=full(crap=4), b=full(crap=4)), snap(a=full(crap=4), b=full(crap=8))))
        self.assertEqual(qr.compare(snap(a=full(crap=9)), snap(a=full(crap=8))), [])
        self.assertIn('average CRAP', qr.compare(snap(), snap(g=full(crap=30)))[0])

    # Regressions from the PR #18 review probes.
    def test_missing_metric_is_not_a_pass(self):
        errors = qr.compare(snap(f=full()), snap(f=dict(cyclomatic=5, cognitive=5)))
        self.assertIn('crap not measured', ' '.join(errors))
        self.assertIn('not measured', ' '.join(qr.compare(snap(), snap(g={}))))

    def test_null_limit_drops_a_metric_by_decision(self):
        self.assertEqual(qr.compare(snap(), snap(g=dict(cyclomatic=5, cognitive=5)),
                                    dict(qr.LIMITS, crap=None)), [])

    def test_deleting_good_units_is_not_a_worsening(self):
        self.assertEqual(qr.compare(snap(a=full(crap=8), b=full(crap=1)), snap(a=full(crap=8))), [])

    def test_metric_absent_from_baseline_meets_absolute_limit(self):
        base = snap(f=dict(cyclomatic=5, crap=3))
        self.assertIn('unbaselined cognitive 50 > limit 15',
                      ' '.join(qr.compare(base, snap(f=dict(cyclomatic=5, cognitive=50, crap=3)))))
        self.assertEqual(qr.compare(base, snap(f=dict(cyclomatic=5, cognitive=9, crap=3))), [])

    def test_non_object_limits_is_input_error(self):
        with tempfile.TemporaryDirectory() as d:
            b, lim = Path(d) / 'b.json', Path(d) / 'l.json'
            b.write_text(json.dumps(snap(f=full()))); lim.write_text('[1]')
            big = subprocess.run([sys.executable, str(SCRIPT), str(b), str(b), '--limits', str(lim)],
                                 capture_output=True, text=True)
            lim.write_text('{"cyclomatic": ' + '9' * 400 + '}')
            big = subprocess.run([sys.executable, str(SCRIPT), str(b), str(b), '--limits', str(lim)],
                                 capture_output=True, text=True)
            self.assertEqual(big.returncode, 2); self.assertNotIn('Traceback', big.stderr)
            lim.write_text('[1]')
            r = subprocess.run([sys.executable, str(SCRIPT), str(b), str(b), '--limits', str(lim)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 2); self.assertNotIn('Traceback', r.stderr)

    def test_non_numeric_metrics_are_input_errors(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'm.json'
            for bad in (dict(f=dict(cyclomatic='3')), dict(f=dict(cyclomatic=True)), dict(f=None),
                        dict(f=dict(cyclomatic=10 ** 400)),
                        dict(f=dict(cyclomatic=float('nan')))):
                with self.subTest(bad=bad):
                    path.write_text(json.dumps(snap(**bad)))
                    with self.assertRaises(ValueError):
                        qr.load(path)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            b, c = Path(d) / 'b.json', Path(d) / 'c.json'
            b.write_text(json.dumps(snap(f=full(c=20)))); c.write_text(json.dumps(snap(f=full(c=18))))
            run = lambda: subprocess.run([sys.executable, str(SCRIPT), str(b), str(c)], capture_output=True).returncode
            self.assertEqual(run(), 0)
            c.write_text(json.dumps(snap(f=full(c=18), g=full(c=12)))); self.assertEqual(run(), 1)
            c.write_text(json.dumps(snap(f=dict(cyclomatic=18)))); self.assertEqual(run(), 1)
            c.write_text(json.dumps(snap(f=dict(cyclomatic='x')))); self.assertEqual(run(), 2)
            c.write_text('{"units": 1}'); self.assertEqual(run(), 2)


if __name__ == '__main__':
    unittest.main()
