import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / 'run_scenarios.py'
spec = importlib.util.spec_from_file_location('run_scenarios', SCRIPT)
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)

OK_EXECUTOR = '''python3 -c "import sys,json; sys.stdin.read(); print('noise ' + json.dumps({'skill':'{model}','first_actions':['a','b','c','d'],'refusals':[],'rationale':'r'}))"'''


def call(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = rs.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class RunScenarioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def run_dir(self, executor, *extra):
        code, _, _ = call('run', '--executor', executor, '--model', 'm/1', '--host', 'h',
                          '--out', self.out, '--timeout', '5', *extra)
        self.assertEqual(code, 0)
        (path,) = Path(self.out).iterdir()
        return path

    def test_prompt_excludes_expect(self):
        _, scenarios = rs.load_scenarios()
        for s in scenarios:
            prompt = rs.render_prompt(s)
            self.assertNotIn('"must"', prompt)
            for item in s['expect'].get('must', []):
                self.assertNotIn(item, prompt)
            self.assertIn('Situation: ' + s['situation'], prompt)
            self.assertIn('Owner message: ' + s['user'], prompt)

    def test_role_scenarios_get_role_note(self):
        _, scenarios = rs.load_scenarios()
        for s in scenarios:
            self.assertEqual(rs.ROLE_NOTE in rs.render_prompt(s), s['situation'].startswith('Rendered'))

    def test_only_filter(self):
        _, scenarios = rs.load_scenarios()
        ids = [s['id'] for s in rs.filter_scenarios(scenarios, 'S1,S6-gate-skip')]
        self.assertEqual(ids, ['S1-empty-repo', 'S6-gate-skip'])
        self.assertEqual([s['id'] for s in rs.filter_scenarios(scenarios, 'S1-')], ['S1-empty-repo'])
        self.assertEqual(len(rs.filter_scenarios(scenarios, None)), len(scenarios))

    def test_dry_run_writes_nothing(self):
        code, out, _ = call('run', '--executor', 'false', '--model', 'm', '--host', 'h',
                            '--out', self.out, '--only', 'S1-', '--dry-run')
        self.assertEqual(code, 0)
        self.assertIn('Owner message:', out)
        self.assertEqual(list(Path(self.out).iterdir()), [])

    def test_fake_executor_makes_well_formed_run(self):
        path = self.run_dir(OK_EXECUTOR, '--only', 'S1-', '--repeats', '2')
        self.assertTrue(path.name.endswith('-h-m-1'))
        manifest = json.loads((path / 'manifest.json').read_text())
        for key in ('utc', 'host', 'model', 'executor', 'git_head', 'git_dirty', 'dist_sha256',
                    'scenarios_version', 'python'):
            self.assertIn(key, manifest)
        self.assertEqual(len(manifest['dist_sha256']) > 0, True)
        rec = json.loads((path / 'S1-empty-repo.r2.json').read_text())
        self.assertFalse(rec['plumbing_failure'])
        self.assertEqual(rec['parsed']['skill'], 'm/1')
        self.assertEqual(rec['exit_code'], 0)
        self.assertIsNone(rec['verdict'])

    def test_failing_and_timeout_executors_are_plumbing(self):
        path = self.run_dir('exit 3', '--only', 'S1-')
        rec = json.loads((path / 'S1-empty-repo.r1.json').read_text())
        self.assertTrue(rec['plumbing_failure'])
        self.assertEqual(rec['exit_code'], 3)
        code, _, _ = call('run', '--executor', 'sleep 5', '--model', 'm', '--host', 't',
                          '--out', self.out, '--only', 'S1-', '--timeout', '0.5')
        self.assertEqual(code, 0)
        rec = json.loads(next(p for p in Path(self.out).glob('*-t-m/S1-*.json')).read_text())
        self.assertTrue(rec['timed_out'])
        self.assertTrue(rec['plumbing_failure'])

    def test_no_json_is_plumbing(self):
        path = self.run_dir('cat >/dev/null; echo hello', '--only', 'S1-')
        rec = json.loads((path / 'S1-empty-repo.r1.json').read_text())
        self.assertIsNone(rec['parsed'])
        self.assertTrue(rec['plumbing_failure'])

    def test_grade_and_plumbing_rule(self):
        good = self.run_dir(OK_EXECUTOR, '--only', 'S1-')
        code, _, _ = call('grade', str(good), 'S1-empty-repo', 'PASS', '--by', 'me', '--notes', 'ok')
        self.assertEqual(code, 0)
        rec = json.loads((good / 'S1-empty-repo.r1.json').read_text())
        self.assertEqual((rec['verdict'], rec['graded_by'], rec['notes']), ('PASS', 'me', 'ok'))
        bad = good.parent / 'bad'
        bad.mkdir()
        (good / 'manifest.json').rename(bad / 'manifest.json')
        rec['plumbing_failure'], rec['verdict'] = True, None
        (bad / 'S1-empty-repo.r1.json').write_text(json.dumps(rec))
        code, _, _ = call('grade', str(bad), 'S1-empty-repo', 'PASS', '--by', 'me')
        self.assertEqual(code, 1)
        code, _, _ = call('grade', str(bad), 'S1-empty-repo', 'UNKNOWN', '--by', 'me')
        self.assertEqual(code, 0)
        code, _, _ = call('grade', str(bad), 'S9-nope', 'UNKNOWN', '--by', 'me')
        self.assertEqual(code, 2)

    def test_report_renders(self):
        path = self.run_dir(OK_EXECUTOR, '--only', 'S1-')
        code, out, _ = call('report', str(path))
        self.assertEqual(code, 0)
        self.assertIn('| S1-empty-repo | selection | 1 | ungraded | no |', out)
        self.assertIn('must: ', out)
        self.assertIn('a; b; c', out)
        self.assertNotIn('d |', out.split('first actions:')[1].split('\n')[0])


if __name__ == '__main__':
    unittest.main()
