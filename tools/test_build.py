import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / 'build.py'
spec = importlib.util.spec_from_file_location('build', SCRIPT)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def tree(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def files(self, extra=None):
        tree(self.root, {'core/references/gate.md': 'policy', 'core/scripts/v.py': '',
                         'new-product/SKILL.md': 'see `references/gate.md`', **(extra or {})})
        return build.package_files(self.root, 'new-product')

    def test_repository_packages_are_clean(self):
        packages, errors = build.build()
        self.assertEqual(errors, [])
        self.assertEqual(set(packages), set(build.SKILLS))

    def test_core_is_identical_in_both_packages(self):
        packages, _ = build.build()
        (a, _), (b, _) = packages.values()
        core = {rel for rel, src in a.items() if src.relative_to(build.ROOT).parts[0] == 'core'}
        self.assertIn('scripts/validate_gate.py', core)
        self.assertTrue(core <= set(b))
        for rel in core:
            self.assertEqual(a[rel].read_bytes(), b[rel].read_bytes(), rel)

    def test_skill_file_cannot_shadow_core(self):
        with self.assertRaises(ValueError):
            self.files({'new-product/references/gate.md': 'shadow'})

    def test_valid_local_reference_passes(self):
        self.assertEqual(build.link_errors(self.files()), [])

    def test_missing_quoted_reference_fails(self):
        files = self.files({'new-product/SKILL.md': 'load `references/absent.md` first'})
        self.assertIn('missing package-local target: references/absent.md',
                      ' '.join(build.link_errors(files)))

    def test_skill_root_prefix_is_checked(self):
        files = self.files({'new-product/SKILL.md': 'run `python3 <skill-root>/scripts/gone.py x`'})
        self.assertTrue(build.link_errors(files))

    def test_prose_and_project_paths_are_not_package_links(self):
        files = self.files({'new-product/SKILL.md':
                            'Repository scripts/tooling; write `SPEC_PLAN/gates/3.1.json`.'})
        self.assertEqual(build.link_errors(files), [])

    def test_markdown_link_escaping_package_fails(self):
        files = self.files({'new-product/SKILL.md': '[x](../../outside.md)'})
        self.assertIn('escapes package', ' '.join(build.link_errors(files)))

    def test_relative_markdown_link_resolves_from_linking_file(self):
        files = self.files({'core/references/a.md': '[g](gate.md) [h](https://x.y)'})
        self.assertEqual(build.link_errors(files), [])

    def test_package_bytes_are_deterministic(self):
        files = self.files()
        self.assertEqual(build.tar_bytes(files), build.tar_bytes(files))

    def test_package_contains_core_and_skill_at_root(self):
        blob = build.tar_bytes(self.files())
        with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as tar:
            self.assertEqual(sorted(tar.getnames()), ['SKILL.md', 'references/gate.md', 'scripts/v.py'])

    def test_failing_package_tests_are_reported(self):
        files = self.files({'core/tests/test_x.py':
                            'import unittest\nclass T(unittest.TestCase):\n'
                            '    def test_f(self): self.fail("boom")\n'})
        self.assertTrue(build.selftest_package(build.tar_bytes(files), 'p'))


if __name__ == '__main__':
    unittest.main()
