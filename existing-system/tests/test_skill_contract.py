"""existing-system SKILL.md: the D7 step table covers every role, both Consistency checks and the gates."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def reference(name):
    """Installed package: references/<name>; source repository: core/references/<name>."""
    return next(p for p in (ROOT / 'references' / name, ROOT.parent / 'core' / 'references' / name) if p.exists())


class StepTableTests(unittest.TestCase):
    def setUp(self):
        text = (ROOT / 'SKILL.md').read_text()
        self.table = text.split('## Flow', 1)[1].split('Every slice:', 1)[0]

    def test_every_role_has_a_step(self):
        for role in ('Coordinator', 'Archaeology', 'Product', 'Consistency (`product`)', 'Architect',
                     'Tech Lead', 'Consistency (`full`)', 'Developer', 'QA', 'Retro', 'owner'):
            with self.subTest(role=role):
                self.assertIn(role, self.table)

    def test_steps_zero_to_eight_with_gates(self):
        rows = [l for l in self.table.splitlines() if l.startswith('| ') and l[2:3].isdigit()]
        self.assertEqual([r.split('|')[1].strip() for r in rows], [str(i) for i in range(9)])
        for gate in ('READ-ONLY COMPLETE', '`parity`', 'OBS decision', 'initiative receipt', 'owner approval'):
            with self.subTest(gate=gate):
                self.assertIn(gate, self.table)

    def test_index_is_created_before_characterization(self):
        rows = {r.split('|')[1].strip(): r for r in self.table.splitlines() if r.startswith('| ') and r[2:3].isdigit()}
        self.assertIn('specs/INDEX.md', rows['4'])
        self.assertIn('characterization', rows['5'])
        self.assertIn('OBS-n', rows['5'])

    def test_obs_label_without_index_row_fails_index_check(self):
        import importlib.util, tempfile
        script = next(p for p in (ROOT / 'scripts' / 'check_index.py', ROOT.parent / 'core' / 'scripts' / 'check_index.py')
                      if p.exists())
        spec = importlib.util.spec_from_file_location('check_index', script)
        ci = importlib.util.module_from_spec(spec); spec.loader.exec_module(ci)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'specs'; root.mkdir()
            (root / 'INDEX.md').write_text('| ID | Status | Behavior | Verify | Evidence | Origin |\n|---|---|---|---|---|---|\n'
                                           '| OBS-001 | active | When x Then y | spec | | OBS |\n')
            (root / 'test_obs.py').write_text('t("req:OBS-001")\nt("req:OBS-002")\n')
            rows = ci.parse_index((root / 'INDEX.md').read_text())
            errors = ci.check(rows, ci.scan_labels(root, (root / 'INDEX.md').resolve()))
        self.assertTrue(any('req:OBS-002 not in INDEX' in e for e in errors), errors)

    def test_requirements_come_from_index_not_prd(self):
        role_inputs = reference('role-inputs.md').read_text()
        row = next(l for l in role_inputs.splitlines() if l.startswith('| ACTIVE_CRITERIA'))
        self.assertIn('existing-system: `specs/INDEX.md` from the Product delta on, regardless of Released or PRD', row)
        contract = reference('specs-contract.md').read_text()
        self.assertIn('| existing-system | `specs/INDEX.md` from the Product delta on', contract)


if __name__ == '__main__':
    unittest.main()
