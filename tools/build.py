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
CODE_SPAN = re.compile(r'`([^`\n]+)`')
LOCAL = re.compile(r'(?:^|[\s(])(?:<skill-root>/)?((?:references|scripts|tests)/[\w.-]+(?:/[\w.-]+)*)')
MD_LINK = re.compile(r'\]\(([^)\s]+)\)')
EXTERNAL = re.compile(r'^(?:[a-z]+:|#|/|<)|\{\{')


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


def link_errors(files):
    """Package-local references must exist inside the package; relative links must not escape."""
    errors = []
    for rel, src in files.items():
        if not rel.endswith('.md'):
            continue
        text = src.read_text(encoding='utf-8')
        # Skill-root paths quoted as code, e.g. `references/x.md` or `<skill-root>/scripts/y.py`.
        targets = {m for span in CODE_SPAN.findall(text) for m in LOCAL.findall(span)}
        # Markdown links resolve relative to the linking file.
        for link in MD_LINK.findall(text):
            if EXTERNAL.search(link):
                continue
            parts = []
            for part in (PurePosixPath(rel).parent / link.split('#', 1)[0]).parts:
                if part == '..':
                    if not parts:
                        errors.append(f'{rel}: link escapes package: {link}')
                        break
                    parts.pop()
                elif part != '.':
                    parts.append(part)
            else:
                targets.add('/'.join(parts))
        for target in sorted(t.rstrip('.') for t in targets):
            if target not in files and not any(f.startswith(target + '/') for f in files):
                errors.append(f'{rel}: missing package-local target: {target}')
    return errors


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
