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

    def test_requirements_come_from_index_not_prd(self):
        role_inputs = reference('role-inputs.md').read_text()
        row = next(l for l in role_inputs.splitlines() if l.startswith('| ACTIVE_CRITERIA'))
        self.assertIn('existing-system: `specs/INDEX.md` from the Product delta on, regardless of Released or PRD', row)
        contract = reference('specs-contract.md').read_text()
        self.assertIn('| existing-system | `specs/INDEX.md` from the Product delta on', contract)


if __name__ == '__main__':
    unittest.main()
