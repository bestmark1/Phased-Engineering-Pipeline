#!/usr/bin/env python3
"""Validate declared phase evidence; does not execute checks or authorize actions."""
import argparse
import json
from pathlib import Path
import re
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and all(text(item) for item in value)


def unresolved(prompt):
    return sorted(set(re.findall(r'\{\{\s*([^{}]+?)\s*\}\}', prompt)))


def validate(receipt):
    require(isinstance(receipt, dict), 'receipt must be an object')
    require(type(receipt.get('schema_version')) is int and receipt['schema_version'] == 1,
            'unsupported schema_version')
    require(text(receipt.get('phase')) and text(receipt.get('snapshot')), 'phase and snapshot required')
    require(type(receipt.get('strict_mode')) is bool, 'strict_mode must be boolean')
    required = receipt.get('required_gates')
    require(strings(required) and required, 'required_gates must be a nonempty string list')
    require(len(set(required)) == len(required), 'duplicate required gates')
    gates = receipt.get('gates')
    require(isinstance(gates, list), 'gates must be a list')
    seen, exceptions = set(), []
    for record in gates:
        require(isinstance(record, dict), 'gate must be an object')
        name = record.get('id')
        require(text(name), 'gate id required')
        require(name not in seen, f'{name}: duplicate gate')
        seen.add(name)
        require(record.get('snapshot') == receipt['snapshot'], f'{name}: stale snapshot')
        require(text(record.get('evidence')), f'{name}: evidence required')
        status = record.get('status')
        require(status in ('PASS', 'FAIL', 'UNKNOWN'), f'{name}: invalid status')
        kind = record.get('kind')
        require(kind in ('command', 'review', 'approval'), f'{name}: invalid kind')
        require(kind == 'command' or 'baseline_exception' not in record,
                f'{name}: only test commands may have baseline exceptions')
        if kind == 'command':
            require(text(record.get('command')), f'{name}: command required')
            code, failures = record.get('exit_code'), record.get('failures')
            require(type(code) is int, f'{name}: check was not executed or exit code invalid')
            require(strings(failures), f'{name}: failures must list test identities and signatures')
            require(status == ('PASS' if code == 0 else 'FAIL'), f'{name}: status disagrees with exit code')
            if code == 0:
                require(not failures and 'baseline_exception' not in record,
                        f'{name}: successful command cannot have failures/exception')
            else:
                require(code > 0, f'{name}: interrupted process cannot use a baseline exception')
                waiver = record.get('baseline_exception')
                require(isinstance(waiver, dict), f'{name}: failed command without approved exception')
                require(waiver.get('test_only') is True, f'{name}: exception restricted to legacy tests')
                for field in ('baseline_snapshot', 'scope', 'approval', 'evidence'):
                    require(text(waiver.get(field)), f'{name}: exception missing {field}')
                baseline = waiver.get('failures')
                require(strings(baseline) and baseline and failures, f'{name}: empty baseline/current failures')
                require(set(failures) <= set(baseline), f'{name}: new test identity or failure signature')
                exceptions.append(name)
        elif kind == 'approval':
            require(status == 'PASS' and record.get('decision') in ('approved', 'reused'),
                    f'{name}: missing approval')
        else:
            require(text(record.get('rubric_version')), f'{name}: rubric_version required')
            findings = record.get('findings')
            require(isinstance(findings, list), f'{name}: findings list required')
            blocked, unknown = False, False
            for finding in findings:
                require(isinstance(finding, dict), f'{name}: invalid finding')
                for field in ('criterion', 'evidence', 'fix'):
                    require(text(finding.get(field)), f'{name}: finding missing {field}')
                fs, severity = finding.get('status'), finding.get('severity')
                require(fs in ('FAIL', 'UNKNOWN'), f'{name}: invalid finding status')
                require(severity in ('blocking', 'major', 'minor'), f'{name}: invalid severity')
                blocked |= fs == 'FAIL' and (severity == 'blocking' or
                                            (severity == 'major' and receipt['strict_mode']))
                unknown |= fs == 'UNKNOWN'
            expected = 'FAIL' if blocked else 'UNKNOWN' if unknown else 'PASS'
            require(status == expected, f'{name}: verdict disagrees with findings')
            require(status == 'PASS', f'{name}: unresolved review ({status})')
    require(seen == set(required), 'gate set differs from required_gates')
    return exceptions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompt', action='store_true', help='check rendered brief for unresolved tokens')
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    try:
        content = args.path.read_text(encoding='utf-8')
        if args.prompt:
            remaining = unresolved(content)
            require(not remaining, 'unresolved placeholders: ' + ', '.join(remaining))
            print('PASS: no unresolved template tokens')
        else:
            try:
                receipt = json.loads(content)
            except json.JSONDecodeError as exc:
                print(f'INPUT ERROR: {exc}', file=sys.stderr)
                return 2
            exceptions = validate(receipt)
            suffix = '; agreed baseline exceptions: ' + ', '.join(exceptions) if exceptions else ''
            print('ELIGIBLE: declared gate receipt accepted' + suffix)
        return 0
    except (OSError, UnicodeError) as exc:
        print(f'INPUT ERROR: {exc}', file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
