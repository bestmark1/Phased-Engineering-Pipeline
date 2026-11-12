import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / 'check_install.py'
spec = importlib.util.spec_from_file_location('check_install', SCRIPT)
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

FILES = {'SKILL.md': 'skill', 'scripts/a.py': 'print(1)'}


def call(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = ci.main(list(argv))
    return code, out.getvalue(), err.getvalue()


def write_tree(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


class CheckInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.dist = self.base / 'dist'
        self.dist.mkdir()
        with tarfile.open(self.dist / 'demo.skill', 'w:gz') as tar:
            for rel, text in FILES.items():
                data = text.encode()
                info = tarfile.TarInfo(rel)
                info.size = len(data)
                import io as _io
                tar.addfile(info, _io.BytesIO(data))

    def tearDown(self):
        self.tmp.cleanup()

    def root(self, name, files=None):
        root = self.base / name
        root.mkdir()
        if files is not None:
            write_tree(root / 'demo', files)
        return root

    def statuses(self, *roots):
        args = [a for r in roots for a in ('--root', str(r))]
        code, out, _ = call(*args, '--dist', str(self.dist), '--json')
        return code, {Path(r['root']).name: r for r in json.loads(out)}

    def test_match_ignores_pycache(self):
        root = self.root('ok', {**FILES, '__pycache__/x.cpython-311.pyc': 'b', 'scripts/__pycache__/y.pyc': 'b'})
        code, res = self.statuses(root)
        self.assertEqual((code, res['ok']['status']), (0, 'MATCH'))

    def test_missing(self):
        code, res = self.statuses(self.root('empty'))
        self.assertEqual((code, res['empty']['status']), (1, 'MISSING'))

    def test_differs_lists_all_kinds(self):
        root = self.root('bad', {'SKILL.md': 'changed', 'extra.md': 'x'})
        code, res = self.statuses(root)
        self.assertEqual(code, 1)
        diffs = {(d['kind'], d['path']) for d in res['bad']['diffs']}
        self.assertEqual(diffs, {('only-in-dist', 'scripts/a.py'), ('only-installed', 'extra.md'),
                                 ('content', 'SKILL.md')})

    def test_diff_list_is_capped(self):
        root = self.root('many', {**FILES, **{f'n{i}.md': 'x' for i in range(15)}})
        _, res = self.statuses(root)
        self.assertEqual(len(res['many']['diffs']), 10)
        self.assertEqual(res['many']['diff_total'], 15)

    def test_human_output_and_nothing_written(self):
        good = self.root('good', FILES)
        bad = self.root('bad', {'SKILL.md': 'changed'})
        before = sorted(p.relative_to(self.base) for p in self.base.rglob('*'))
        code, out, _ = call('--root', str(good), '--root', str(bad), '--dist', str(self.dist))
        self.assertEqual(code, 1)
        self.assertIn(f'MATCH   {good}/demo', out)
        self.assertIn(f'DIFFERS {bad}/demo', out)
        self.assertIn('    content: SKILL.md', out)
        self.assertEqual(before, sorted(p.relative_to(self.base) for p in self.base.rglob('*')))

    def test_unreadable_dist(self):
        code, _, _ = call('--root', str(self.base), '--dist', str(self.base / 'nope'))
        self.assertEqual(code, 2)
        (self.dist / 'broken.skill').write_bytes(b'not a tar')
        code, _, _ = call('--root', str(self.base), '--dist', str(self.dist))
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
