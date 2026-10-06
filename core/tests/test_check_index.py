import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'check_index.py'
spec = importlib.util.spec_from_file_location('check_index', SCRIPT)
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

HEADER = '| ID | Status | Behavior | Verify | Evidence | Origin |\n|---|---|---|---|---|---|\n'


def row(rid='AC-001', status='active', behavior='Given a user When they log in Then the name shows',
        verify='spec', evidence='', origin='PRD'):
    return f'| {rid} | {status} | {behavior} | {verify} | {evidence} | {origin} |\n'


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'specs'
        self.root.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, rows, spec_text='def test_login(): tag("req:AC-001")\n'):
        (self.root / 'INDEX.md').write_text('# Requirements\n\n' + HEADER + ''.join(rows))
        (self.root / 'test_login.py').write_text(spec_text)
        labels = ci.scan_labels(self.root, (self.root / 'INDEX.md').resolve())
        return ci.check(ci.parse_index((self.root / 'INDEX.md').read_text()), labels)

    def assertFinding(self, errors, needle):
        self.assertTrue(any(needle in e for e in errors), errors)

    def test_traced_registry_passes(self):
        self.assertEqual(self.run_check([row()]), [])

    def test_active_without_spec_fails(self):
        self.assertFinding(self.run_check([row(), row('AC-002')]), 'AC-002: active, no executable spec')

    def test_label_to_unknown_id_fails(self):
        self.assertFinding(self.run_check([row()], 'x = "req:AC-001"\ny = "req:AC-009"\n'), 'req:AC-009 not in INDEX')

    def test_label_to_retired_fails(self):
        errors = self.run_check([row(), row('AC-002', status='retired')], 'a="req:AC-001"\nb="req:AC-002"\n')
        self.assertFinding(errors, 'retired requirement')

    def test_label_only_in_comment_does_not_count(self):
        for comment in ('# "req:AC-001"', '// "req:AC-001"', '  * "req:AC-001"'):
            with self.subTest(comment=comment):
                self.assertFinding(self.run_check([row()], comment + '\n'), 'AC-001: active, no executable spec')

    def test_unquoted_mention_does_not_count(self):
        self.assertFinding(self.run_check([row()], 'covers req:AC-001 somewhere\n'), 'no executable spec')

    # Inputs from the PR #18 review probes.
    def test_documented_title_label_counts(self):
        self.assertEqual(self.run_check([row()], 'test("req:AC-001 shows name", () => {})\n'), [])

    def test_inline_and_block_comments_do_not_count(self):
        for text in ('run(); // "req:AC-001"\n', 'x = 1  # "req:AC-001"\n', '/*\n "req:AC-001"\n*/\n',
                     '<!-- "req:AC-001" -->\n'):
            with self.subTest(text=text):
                self.assertFinding(self.run_check([row()], text), 'no executable spec')

    def test_mismatched_quotes_do_not_count(self):
        self.assertFinding(self.run_check([row()], 'x = "req:AC-001\'\n'), 'no executable spec')

    def test_hash_or_slashes_inside_strings_keep_the_label(self):
        self.assertEqual(self.run_check([row()], 'u = "http://a#b"; t("req:AC-001")\n'), [])

    def test_text_files_in_specs_do_not_count(self):
        (self.root / 'README.md').write_text('Use "req:AC-001" in tests.\n')
        self.assertFinding(self.run_check([row()], 'nothing\n'), 'no executable spec')

    def test_data_support_docstring_and_dash_comments_do_not_count(self):
        (self.root / 'support').mkdir()
        files = {'support/helpers.py': 'TAG = "req:AC-001"\n', 'fixtures.json': '{"tags": ["req:AC-001"]}\n',
                 'data.yaml': '- "req:AC-001"\n', 'seed.sql': 'SELECT 1; -- "req:AC-001"\n',
                 't.lua': 'local x = 1 -- "req:AC-001"\n'}
        for rel, body in files.items():
            (self.root / rel).write_text(body)
        self.assertFinding(self.run_check([row()], 'def test_x():\n    """req:AC-001 covered here"""\n'),
                           'no executable spec')

    def test_label_after_docstring_still_counts(self):
        self.assertEqual(self.run_check([row()], 'def t():\n    """doc"""\n    tag("req:AC-001")\n'), [])

    # Final Codex review of PR #18.
    def test_lua_haskell_blocks_and_nested_quotes_do_not_count(self):
        for name, body in (('t.lua', '--[[\n"req:AC-001"\n]]\n'), ('t.hs', '{-\n"req:AC-001"\n-}\n'),
                           ('t.py', 'x = "\'req:AC-001\'"\n')):
            with self.subTest(name=name):
                (self.root / 'test_login.py').unlink(missing_ok=True)
                for old in self.root.glob('t.*'):
                    old.unlink()
                (self.root / name).write_text(body)
                labels = ci.scan_labels(self.root, (self.root / 'INDEX.md').resolve())
                self.assertNotIn('AC-001', labels)

    def test_missing_separator_is_input_error(self):
        with self.assertRaises(ValueError):
            ci.parse_index(HEADER.splitlines()[0] + '\n' + row())

    # Trial finding F8: requirements whose specs arrive in a later slice.
    def test_planned_rows_need_no_spec_yet(self):
        self.assertEqual(self.run_check([row(), row('AC-002', status='planned')]), [])

    def test_label_on_planned_row_fails_until_activated(self):
        errors = self.run_check([row(), row('AC-002', status='planned')], 'a="req:AC-001"\nb="req:AC-002"\n')
        self.assertFinding(errors, 'points to a planned requirement')
        self.assertEqual(self.run_check([row(), row('AC-002')], 'a="req:AC-001"\nb="req:AC-002"\n'), [])

    def test_final_check_rejects_planned_rows(self):
        """PR #20 review P1: an initiative must not complete with approved criteria left planned."""
        rows = [row(), row('AC-002', status='planned')]
        self.assertEqual(self.run_check(rows), [])
        (self.root / 'INDEX.md').write_text('# R\n\n' + HEADER + ''.join(rows))
        labels = ci.scan_labels(self.root, (self.root / 'INDEX.md').resolve())
        errors = ci.check(ci.parse_index((self.root / 'INDEX.md').read_text()), labels, final=True)
        self.assertTrue(any('AC-002: still planned' in e for e in errors), errors)

    def test_planned_rows_still_need_valid_schema(self):
        self.assertFinding(self.run_check([row(), row('AC-002', status='planned', verify='manual')]), 'verify')

    def test_spec_behavior_needs_when_then(self):
        self.assertFinding(self.run_check([row(behavior='User sees name')]), 'must state When and Then')

    def test_non_spec_verification_needs_evidence(self):
        errors = self.run_check([row(), row('QR-001', behavior='No secrets in logs', verify='static')])
        self.assertFinding(errors, 'QR-001: static verification needs an evidence reference')
        self.assertEqual(self.run_check([row(), row('QR-001', behavior='No secrets', verify='static',
                                                     evidence='`make secrets-scan`')]), [])

    def test_schema_errors(self):
        for bad, needle in ((row('AC-1x'), 'invalid ID'), (row(status='done'), 'status'),
                            (row(verify='manual'), 'verify'), (row(origin='chat'), 'origin'),
                            (row(behavior=''), 'behavior required')):
            with self.subTest(needle=needle):
                self.assertFinding(self.run_check([bad]), needle)
        self.assertFinding(self.run_check([row(), row()]), 'duplicate ID')

    def test_obs_and_deviation_origins_are_valid(self):
        rows = [row(), row('OBS-001', origin='OBS'), row('AC-002', origin='deviation:OBS-001')]
        spec_text = 'a="req:AC-001"\nb="req:OBS-001"\nc="req:AC-002"\n'
        self.assertEqual(self.run_check(rows, spec_text), [])

    def test_missing_table_is_input_error(self):
        with self.assertRaises(ValueError):
            ci.parse_index('# no table here')

    def test_cli_exit_codes(self):
        self.run_check([row()])
        args = [sys.executable, str(SCRIPT), '--index', str(self.root / 'INDEX.md'), '--specs', str(self.root)]
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
        (self.root / 'test_login.py').write_text('nothing\n')
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 1)
        (self.root / 'INDEX.md').write_text('broken')
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
