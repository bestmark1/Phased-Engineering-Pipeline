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

    def test_every_reference_has_a_load_point(self):
        """Each references/*.md is named in SKILL.md or pipeline-core.md, where its load condition is stated."""
        packages, _ = build.build()
        for name, (files, _) in packages.items():
            entry = files['SKILL.md'].read_text() + files['references/pipeline-core.md'].read_text()
            for rel in files:
                if rel.startswith('references/') and rel.endswith('.md'):
                    with self.subTest(package=name, ref=rel):
                        self.assertIn(rel, entry)

    def test_every_role_prompt_requires_the_pipeline_context_block(self):
        """Seam audit G1-G19: role prompts are pipeline-agnostic; the coordinator must append the block."""
        packages, _ = build.build()
        for name, (files, _) in packages.items():
            role_inputs = files['references/role-inputs.md'].read_text()
            self.assertIn('## Pipeline context block', role_inputs)
            self.assertIn('pipeline context block', files['SKILL.md'].read_text())
            for rel in files:
                if rel.startswith('references/') and rel.endswith('-prompt.md') and rel != 'references/entry-prompt.md':
                    text = files[rel].read_text()
                    with self.subTest(package=name, prompt=rel):
                        self.assertIn('pipeline context block', text)
                        self.assertNotRegex(text, r'Replace[^\n]*\{\{[A-Z_]+\}\}[^\n]*before sending')

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

    def assertFlags(self, skill_md, needle):
        errors = ' '.join(build.link_errors(self.files({'new-product/SKILL.md': skill_md})))
        self.assertIn(needle, errors)

    def assertClean(self, skill_md):
        self.assertEqual(build.link_errors(self.files({'new-product/SKILL.md': skill_md})), [])

    # Cases from the PR #17 review.
    def test_skill_root_path_escaping_package_fails(self):
        self.assertFlags('`<skill-root>/../outside.md`', 'escapes package')

    def test_skill_root_path_outside_package_dirs_is_checked(self):
        self.assertFlags('`<skill-root>/absent.txt`', 'missing package-local target: absent.txt')

    def test_fenced_code_paths_are_checked(self):
        self.assertFlags('```bash\npython3 scripts/missing.py\n```\n', 'scripts/missing.py')

    def test_angle_bracket_markdown_link_is_checked(self):
        self.assertFlags('[x](<scripts/missing.py>)', 'scripts/missing.py')

    def test_project_markdown_link_is_not_package_local(self):
        self.assertClean('[p](SPEC_PLAN/PRD.md) [d](docs/x.md)')

    def test_package_path_is_normalized(self):
        self.assertClean('`references/../scripts/v.py`')

    def test_placeholders_in_code_are_ignored(self):
        self.assertClean('`<skill-root>/scripts/v.py <project>/SPEC_PLAN/gates/<phase>.json`')

    # Cases from the second PR #17 review round.
    def test_tilde_indented_and_unclosed_fences_are_checked(self):
        for md in ('~~~\npython3 scripts/missing.py\n~~~\n',
                   '  ```bash\n  python3 scripts/missing.py\n  ```\n',
                   '```\npython3 scripts/missing.py\n'):
            with self.subTest(md=md):
                self.assertFlags(md, 'scripts/missing.py')

    def test_escaped_angle_bracket_link_resolves(self):
        tree(self.root, {'core/references/a(b).md': ''})
        self.assertClean(r'[ok](<references/a\(b\).md>)')

    def test_balanced_parens_and_title_in_link(self):
        tree(self.root, {'core/references/a(b).md': ''})
        self.assertClean('[ok](references/a(b).md "title")')

    def test_unterminated_link_is_not_a_link(self):
        self.assertClean('[example](scripts/missing.py and more text')

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
