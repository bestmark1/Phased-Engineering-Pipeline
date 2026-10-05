#!/usr/bin/env python3
"""Assemble the two skill packages from core/ + each skill dir; check package-local links."""
import argparse
import gzip
import io
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {'new-product-pipeline': 'new-product', 'existing-system-pipeline': 'existing-system'}
PACKAGE_DIRS = ('references', 'scripts', 'tests')
# CommonMark-ish fences: ``` or ~~~, up to 3 spaces indent, unclosed fence runs to EOF.
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?(?:^ {0,3}\1[ \t]*$|\Z)', re.S | re.M)
CODE_SPAN = re.compile(r'`([^`\n]+)`')
# In code: `<skill-root>/<anything>` or a path starting with a package directory.
CODE_PATH = re.compile(r'(?:^|(?<=[\s("\'=]))(<skill-root>/[^\s`"\')]+|(?:references|scripts|tests)/[^\s`"\')]+)')
# Complete inline link: ](dest) or ](<dest>), optional title, balanced parens, backslash escapes.
MD_LINK = re.compile(r'\]\(\s*(<(?:[^<>\\\n]|\\.)*>|(?:[^\s()\\]|\\.|\((?:[^\s()\\]|\\.)*\))+)'
                     r'(?:\s+(?:"[^"]*"|\'[^\']*\'))?\s*\)')
EXTERNAL = re.compile(r'^(?:[a-z][a-z0-9+.-]*:|#|/)|\{\{')


def package_files(root, skill_dir):
    """Map package path -> source file; a skill file may not shadow a core file."""
    files = {}
    for base in (root / 'core', root / skill_dir):
        for src in sorted(p for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
            rel = src.relative_to(base).as_posix()
            if rel in files:
                raise ValueError(f'{skill_dir}: {rel} collides with core')
            files[rel] = src
    return files


def normalize(path):
    """Collapse . and .. against the package root; None when the path escapes it."""
    parts = []
    for part in PurePosixPath(path).parts:
        if part == '..':
            if not parts:
                return None
            parts.pop()
        elif part not in ('.', ''):
            parts.append(part)
    return '/'.join(parts)


def is_package_path(path):
    return path == 'SKILL.md' or path.split('/', 1)[0] in PACKAGE_DIRS


def link_errors(files):
    """Package-local references must exist inside the package and stay within it.

    Package-local: `<skill-root>/...` or `references|scripts|tests/...` inside inline or
    fenced code, and Markdown links resolving into those directories or SKILL.md.
    Other relative paths (SPEC_PLAN/, specs/, docs/) belong to the target project.
    """
    errors = []
    for rel, src in files.items():
        if not rel.endswith('.md'):
            continue
        text = src.read_text(encoding='utf-8')
        fenced = [m.group(0) for m in FENCE.finditer(text)]
        code = fenced + CODE_SPAN.findall(FENCE.sub('', text))
        candidates = []  # (as written, normalized-or-None)
        for block in code:
            for token in CODE_PATH.findall(block):
                path = token.removeprefix('<skill-root>/').rstrip('.,;:')
                if '<' in path or '{{' in path or '*' in path:
                    continue
                candidates.append((token, normalize(path)))
        for link in MD_LINK.findall(text):
            link = re.sub(r'\\(.)', r'\1', link.removeprefix('<').removesuffix('>')).split('#', 1)[0]
            if not link or EXTERNAL.search(link):
                continue
            target = normalize((PurePosixPath(rel).parent / link).as_posix())
            if target is None or is_package_path(target):
                candidates.append((link, target))
        for written, target in candidates:
            if target is None:
                errors.append(f'{rel}: path escapes package: {written}')
            elif target not in files and not any(f.startswith(target.rstrip('/') + '/') for f in files):
                errors.append(f'{rel}: missing package-local target: {target}')
    return sorted(set(errors))


def tar_bytes(files):
    """Deterministic gzipped tar: sorted entries, fixed metadata."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.PAX_FORMAT) as tar:
        for rel in sorted(files):
            data = files[rel].read_bytes()
            info = tarfile.TarInfo(rel)
            info.size, info.mtime, info.mode = len(data), 0, 0o755 if rel.endswith('.py') else 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ''
            tar.addfile(info, io.BytesIO(data))
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode='wb', mtime=0) as gz:
        gz.write(raw.getvalue())
    return out.getvalue()


def selftest_package(blob, name):
    """Extract into an empty dir; the package must pass its own tests without the repo."""
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as tar:
            tar.extractall(tmp, filter='data')
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q'],
                                cwd=tmp, capture_output=True, text=True,
                                env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
        if result.returncode:
            return [f'{name}: package tests failed in isolation:\n{result.stderr[-2000:]}']
    return []


def build(root=ROOT):
    packages, errors = {}, []
    for name, skill_dir in SKILLS.items():
        files = package_files(root, skill_dir)
        errors += [f'{name}: {e}' for e in link_errors(files)]
        packages[name] = (files, tar_bytes(files))
    core = {p.relative_to(root / 'core').as_posix() for p in (root / 'core').rglob('*') if p.is_file()}
    core.discard('')
    for name, (files, _) in packages.items():
        missing = {c for c in core if '__pycache__' not in c} - set(files)
        if missing:
            errors.append(f'{name}: core files missing: {sorted(missing)}')
    return packages, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='fail if dist/ is stale instead of writing it')
    args = parser.parse_args(argv)
    packages, errors = build()
    for name, (_, blob) in packages.items():
        errors += selftest_package(blob, name)
    dist = ROOT / 'dist'
    for name, (_, blob) in packages.items():
        target = dist / f'{name}.skill'
        if args.check:
            if not target.exists() or target.read_bytes() != blob:
                errors.append(f'{target.relative_to(ROOT)} is stale; run python3 tools/build.py')
        elif not errors:
            dist.mkdir(exist_ok=True)
            target.write_bytes(blob)
    for error in errors:
        print(f'ERROR: {error}', file=sys.stderr)
    if not errors:
        print('OK: ' + ', '.join(f'{n} ({len(f)} files)' for n, (f, _) in packages.items()))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
