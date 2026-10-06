import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'parity.py'
spec = importlib.util.spec_from_file_location('parity', SCRIPT)
parity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parity)

ENV = {'seed': 'fixtures/seed.sql@abc', 'runtime': 'python3.12'}
OLD_LOGIN = dict(outcome='pass', observation='401 {"error":"bad password"}')
NEW_LOGIN = dict(outcome='fail', observation='429 {"error":"locked"}')


def record(results, suite='suite-1', product='p', env=ENV):
    return dict(product_sha=product, suite_sha=suite, environment=dict(env), results=results, exit_code=0)


BASE = record({'login-wrong-password': OLD_LOGIN, 'logout': dict(outcome='pass', observation='204')}, product='old')
DELTA = dict(spec='login-wrong-password', expected_old=OLD_LOGIN, expected_new=NEW_LOGIN, obs='OBS-003', ac='AC-007')
INDEX = {'AC-007': dict(ID='AC-007', Status='active', Origin='deviation:OBS-003')}


class CompareTests(unittest.TestCase):
    def run_of(self, **changes):
        results = dict(BASE['results'], **changes)
        return record(results, product='new')

    def test_identical_behavior_passes(self):
        self.assertEqual(parity.compare(BASE, self.run_of())[0], 'PASS')

    def test_divergence_without_delta_fails(self):
        verdict, reasons = parity.compare(BASE, self.run_of(**{'login-wrong-password': NEW_LOGIN}))
        self.assertEqual(verdict, 'FAIL'); self.assertIn('without an approved delta', reasons[0])

    def test_matching_delta_passes_even_though_frozen_spec_fails(self):
        current = self.run_of(**{'login-wrong-password': NEW_LOGIN}); current['exit_code'] = 1
        self.assertEqual(parity.compare(BASE, current, [DELTA], INDEX)[0], 'PASS')

    def test_delta_without_index_confirmation_fails(self):
        verdict, reasons = parity.compare(BASE, self.run_of(**{'login-wrong-password': NEW_LOGIN}), [DELTA])
        self.assertEqual(verdict, 'FAIL'); self.assertIn('INDEX confirmation', reasons[0])

    def test_duplicate_or_malformed_deltas_are_input_errors(self):
        current = self.run_of(**{'login-wrong-password': NEW_LOGIN})
        bad_deltas = ([DELTA, dict(DELTA, expected_new=dict(outcome='fail', observation='403'))], [DELTA, DELTA],
                      [dict(DELTA, spec=[])], [dict(DELTA, ac=[])], [dict(DELTA, obs='AC-1')],
                      [dict(DELTA, expected_new='429')])
        for deltas in bad_deltas:
            with self.subTest(deltas=deltas), self.assertRaises(parity.InputError):
                parity.compare(BASE, current, deltas, INDEX)

    def test_empty_results_are_input_errors(self):
        with self.assertRaises(parity.InputError):
            parity.compare(record({}), record({}))

    def test_delta_must_match_exact_old_and_new(self):
        other = dict(outcome='fail', observation='500 boom')
        verdict, reasons = parity.compare(BASE, self.run_of(**{'login-wrong-password': other}), [DELTA], INDEX)
        self.assertEqual(verdict, 'FAIL'); self.assertIn('does not match its delta', reasons[0])

    def test_other_suite_sha_fails(self):
        current = self.run_of(); current['suite_sha'] = 'suite-2'
        self.assertEqual(parity.compare(BASE, current)[0], 'FAIL')

    def test_missing_run_or_other_environment_is_unknown(self):
        current = self.run_of(); del current['results']['logout']
        self.assertEqual(parity.compare(BASE, current)[0], 'UNKNOWN')
        current = self.run_of(); current['environment'] = dict(ENV, seed='other')
        self.assertEqual(parity.compare(BASE, current)[0], 'UNKNOWN')

    def test_failure_outranks_unknown(self):
        current = self.run_of(**{'login-wrong-password': NEW_LOGIN}); del current['results']['logout']
        self.assertEqual(parity.compare(BASE, current)[0], 'FAIL')

    def test_delta_must_be_an_approved_deviation_in_index(self):
        current = self.run_of(**{'login-wrong-password': NEW_LOGIN})
        good = {'AC-007': dict(ID='AC-007', Status='active', Origin='deviation:OBS-003')}
        self.assertEqual(parity.compare(BASE, current, [DELTA], good)[0], 'PASS')
        for bad in ({}, {'AC-007': dict(good['AC-007'], Origin='PRD')}, {'AC-007': dict(good['AC-007'], Status='retired')}):
            with self.subTest(index=bad):
                self.assertEqual(parity.compare(BASE, current, [DELTA], bad)[0], 'FAIL')

    def test_malformed_records_are_input_errors(self):
        for bad in ([], dict(BASE, results={'x': dict(outcome='ok', observation='')}), dict(BASE, environment=None)):
            with self.subTest(bad=bad), self.assertRaises(parity.InputError):
                parity.compare(bad, BASE)


SPEC_RUNNER = '''import json, os, pathlib
greeting = pathlib.Path("app.txt").read_text().strip()
results = {"greeting": {"outcome": "pass" if greeting == "%s" else "fail", "observation": greeting}}
pathlib.Path(os.environ["PARITY_RESULTS"]).write_text(json.dumps(results))
raise SystemExit(0 if results["greeting"]["outcome"] == "pass" else 1)
'''


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=t', '-c', 'user.email=t@t',
                               *args], check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, app, expected):
        (self.repo / 'app.txt').write_text(app + '\n')
        (self.repo / 'specs').mkdir(exist_ok=True)
        (self.repo / 'specs' / 'run.py').write_text(SPEC_RUNNER % expected)
        self.git('add', '-A'); self.git('commit', '-q', '-m', app)
        return self.git('rev-parse', 'HEAD')

    def test_frozen_suite_runs_against_new_product(self):
        old = self.commit('hello', 'hello')
        # the new commit changes both the product and its own copy of the specs
        new = self.commit('hi', 'hi')
        cmd = f'{sys.executable} specs/run.py'
        base = parity.run(self.repo, old, old, cmd, ENV)
        now = parity.run(self.repo, old, new, cmd, ENV)  # suite frozen at `old`
        self.assertEqual(base['results']['greeting']['outcome'], 'pass')
        self.assertEqual(now['results']['greeting'], dict(outcome='fail', observation='hi'))
        self.assertEqual(now['exit_code'], 1)  # raw spec exit kept, separate from the verdict
        self.assertEqual(parity.compare(base, now)[0], 'FAIL')
        own_suite = parity.run(self.repo, new, new, cmd, ENV)
        self.assertEqual(own_suite['results']['greeting']['outcome'], 'pass')  # why freezing matters
        self.assertEqual(self.git('worktree', 'list').count('\n'), 0)  # temporary worktree removed

    def test_suite_paths_freeze_support_and_fixtures(self):
        (self.repo / 'fixtures').mkdir()
        (self.repo / 'fixtures' / 'expected.txt').write_text('hello')
        (self.repo / 'specs' ).mkdir()
        (self.repo / 'specs' / 'support').mkdir()
        (self.repo / 'specs' / 'support' / 'helper.py').write_text('EXPECTED_FILE = "fixtures/expected.txt"\n')
        runner = ('import json, os, pathlib, sys\nsys.path.insert(0, "specs/support")\nfrom helper import EXPECTED_FILE\n'
                  'want = pathlib.Path(EXPECTED_FILE).read_text().strip()\n'
                  'got = pathlib.Path("app.txt").read_text().strip()\n'
                  'pathlib.Path(os.environ["PARITY_RESULTS"]).write_text(json.dumps({"g": {"outcome": "pass" if want == got else "fail", "observation": got}}))\n')
        (self.repo / 'specs' / 'run.py').write_text(runner)
        (self.repo / 'app.txt').write_text('hello\n')
        self.git('add', '-A'); self.git('commit', '-q', '-m', 'v1'); old = self.git('rev-parse', 'HEAD')
        # the change edits the product AND the fixture and helper, trying to bless the new behavior
        (self.repo / 'app.txt').write_text('hi\n'); (self.repo / 'fixtures' / 'expected.txt').write_text('hi')
        self.git('add', '-A'); self.git('commit', '-q', '-m', 'v2'); new = self.git('rev-parse', 'HEAD')
        cmd = f'{sys.executable} specs/run.py'
        frozen_specs_only = parity.run(self.repo, old, new, cmd, ENV)
        self.assertEqual(frozen_specs_only['results']['g']['outcome'], 'pass')  # fixture not frozen: hidden
        frozen_all = parity.run(self.repo, old, new, cmd, ENV, ('specs', 'fixtures'))
        self.assertEqual(frozen_all['results']['g']['outcome'], 'fail')  # fixture frozen too: caught

    def test_frozen_helper_and_config_are_the_old_versions(self):
        (self.repo / 'specs' / 'support').mkdir(parents=True)
        (self.repo / 'config').mkdir()
        runner = ('import json, os, pathlib, sys\nsys.path.insert(0, "specs/support")\nimport helper\n'
                  'cfg = pathlib.Path("config/test.json").read_text().strip()\n'
                  'pathlib.Path(os.environ["PARITY_RESULTS"]).write_text(json.dumps('
                  '{"h": {"outcome": "pass", "observation": helper.VERSION + "/" + cfg}}))\n')
        (self.repo / 'specs' / 'run.py').write_text(runner)
        (self.repo / 'app.txt').write_text('x\n')
        for version in ('v1', 'v2'):
            (self.repo / 'specs' / 'support' / 'helper.py').write_text(f'VERSION = "helper-{version}"\n')
            (self.repo / 'config' / 'test.json').write_text(f'cfg-{version}')
            self.git('add', '-A'); self.git('commit', '-q', '-m', version)
            if version == 'v1':
                old = self.git('rev-parse', 'HEAD')
        new = self.git('rev-parse', 'HEAD')
        got = parity.run(self.repo, old, new, f'{sys.executable} specs/run.py', ENV, ('specs', 'config'))
        self.assertEqual(got['results']['h']['observation'], 'helper-v1/cfg-v1')

    def test_suite_path_outside_repository_is_rejected_before_any_removal(self):
        sha = self.commit('hello', 'hello')
        outside = Path(self.tmp.name) / 'outside'; outside.mkdir(); (outside / 'keep.txt').write_text('x')
        for path in (str(outside), '../outside', 'specs/../../outside', '.git', '.GIT', 'specs/.Git/x', '.'):
            with self.subTest(path=path), self.assertRaises(parity.InputError):
                parity.run(self.repo, sha, sha, 'true', ENV, (path,))
        self.assertTrue((outside / 'keep.txt').exists())

    def test_failed_checkout_leaves_no_registered_worktree(self):
        self.commit('hello', 'hello')
        with self.assertRaises(parity.InputError):
            parity.run(self.repo, 'HEAD', 'no-such-commit', 'true', ENV)
        self.assertEqual(self.git('worktree', 'list').count('\n'), 0)

    def test_invalid_results_json_is_input_error(self):
        sha = self.commit('hello', 'hello')
        for bad in ('printf "{" > "$PARITY_RESULTS"', 'mkdir "$PARITY_RESULTS"'):
            with self.subTest(command=bad), self.assertRaises(parity.InputError):
                parity.run(self.repo, sha, sha, bad, ENV)
        self.assertEqual(self.git('worktree', 'list').count('\n'), 0)

    def test_command_without_results_is_input_error(self):
        sha = self.commit('hello', 'hello')
        with self.assertRaises(parity.InputError):
            parity.run(self.repo, sha, sha, 'true', ENV)

    def test_cli_exit_codes(self):
        d = Path(self.tmp.name)
        (d / 'b.json').write_text(json.dumps(BASE))
        (d / 'r.json').write_text(json.dumps(record(dict(BASE['results']), product='new')))
        cli = lambda *a: subprocess.run([sys.executable, str(SCRIPT), *a], capture_output=True, text=True)
        self.assertEqual(cli('compare', str(d / 'b.json'), str(d / 'r.json')).returncode, 0)
        (d / 'r.json').write_text(json.dumps(record({'logout': dict(outcome='pass', observation='204')}, product='new')))
        unknown = cli('compare', str(d / 'b.json'), str(d / 'r.json'))
        self.assertEqual(unknown.returncode, 1); self.assertIn('PARITY UNKNOWN', unknown.stdout)
        # --index: the delta must be an approved deviation in specs/INDEX.md
        (d / 'r.json').write_text(json.dumps(record(dict(BASE['results'], **{'login-wrong-password': NEW_LOGIN}),
                                                    product='new')))
        (d / 'deltas.json').write_text(json.dumps([DELTA]))
        head = '| ID | Status | Behavior | Verify | Evidence | Origin |\n|---|---|---|---|---|---|\n'
        (d / 'INDEX.md').write_text(head + '| AC-007 | active | When locked Then 429 | spec | | deviation:OBS-003 |\n')
        args = ('compare', str(d / 'b.json'), str(d / 'r.json'), '--deltas', str(d / 'deltas.json'), '--index', str(d / 'INDEX.md'))
        self.assertEqual(cli(*args).returncode, 0)
        (d / 'INDEX.md').write_text(head + '| AC-007 | active | When locked Then 429 | spec | | PRD |\n')
        self.assertEqual(cli(*args).returncode, 1)
        missing_index = cli('compare', str(d / 'b.json'), str(d / 'r.json'), '--deltas', str(d / 'deltas.json'),
                            '--index', str(d / 'nope.md'))
        self.assertEqual(missing_index.returncode, 2); self.assertNotIn('Traceback', missing_index.stderr)
        (d / 'r.json').write_text('{')
        broken = cli('compare', str(d / 'b.json'), str(d / 'r.json'))
        self.assertEqual(broken.returncode, 2); self.assertNotIn('Traceback', broken.stderr)


if __name__ == '__main__':
    unittest.main()
