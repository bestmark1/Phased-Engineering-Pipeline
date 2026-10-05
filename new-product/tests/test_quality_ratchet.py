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


def snap(tool='lizard 1.17.10', **units):
    return dict(tool=tool, units=units)


class RatchetTests(unittest.TestCase):
    def test_existing_unit_improving_above_limit_passes(self):
        self.assertEqual(qr.compare(snap(f=dict(cyclomatic=20)), snap(f=dict(cyclomatic=18))), [])

    def test_existing_unit_worsening_fails(self):
        errors = qr.compare(snap(f=dict(cyclomatic=18)), snap(f=dict(cyclomatic=19)))
        self.assertIn('worsened 18 -> 19', errors[0])

    def test_new_unit_over_absolute_limit_fails(self):
        errors = qr.compare(snap(), snap(g=dict(cyclomatic=12)))
        self.assertIn('new unit cyclomatic 12 > limit 10', errors[0])

    def test_new_unit_within_limits_passes(self):
        self.assertEqual(qr.compare(snap(), snap(g=dict(cyclomatic=10, cognitive=15, crap=4))), [])
        self.assertIn("average CRAP", qr.compare(snap(), snap(g=dict(crap=30)))[0])

    def test_tool_version_change_without_new_baseline_fails(self):
        errors = qr.compare(snap(f=dict(cyclomatic=5)), snap('lizard 1.18.0', f=dict(cyclomatic=5)))
        self.assertIn('commit a new baseline', errors[0])

    def test_average_crap_ratchet(self):
        self.assertTrue(qr.compare(snap(a=dict(crap=4), b=dict(crap=4)), snap(a=dict(crap=4), b=dict(crap=8))))
        self.assertEqual(qr.compare(snap(a=dict(crap=9)), snap(a=dict(crap=8))), [])

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            b, c = Path(d) / 'b.json', Path(d) / 'c.json'
            b.write_text(json.dumps(snap(f=dict(cyclomatic=20)))); c.write_text(json.dumps(snap(f=dict(cyclomatic=18))))
            run = lambda: subprocess.run([sys.executable, str(SCRIPT), str(b), str(c)], capture_output=True).returncode
            self.assertEqual(run(), 0)
            c.write_text(json.dumps(snap(f=dict(cyclomatic=18), g=dict(cyclomatic=12)))); self.assertEqual(run(), 1)
            c.write_text('{"units": 1}'); self.assertEqual(run(), 2)


if __name__ == '__main__':
    unittest.main()
