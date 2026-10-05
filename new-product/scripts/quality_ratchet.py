#!/usr/bin/env python3
"""Compare per-unit quality metrics with the committed baseline (references/quality-profile.md).

New units must meet absolute limits; existing units must not get worse; a different measuring
tool/version needs a new baseline commit. Input JSON: {"tool": "lizard 1.17.10",
"units": {"src/a.py::f": {"cyclomatic": 7, "cognitive": 9, "crap": 4.0}}}.
Exit 0 = pass, 1 = violations, 2 = bad input.
"""
import argparse
import json
from pathlib import Path
import sys

LIMITS = {'cyclomatic': 10, 'cognitive': 15, 'crap': 30}
CRAP_AVG = 5


def load(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('tool'), str) or not isinstance(data.get('units'), dict):
        raise ValueError(f'{path}: expected {{"tool": str, "units": {{...}}}}')
    return data


def average_crap(units):
    values = [m['crap'] for m in units.values() if isinstance(m.get('crap'), (int, float))]
    return sum(values) / len(values) if values else 0.0


def compare(baseline, current, limits=LIMITS, crap_avg=CRAP_AVG):
    if baseline['tool'] != current['tool']:
        return [f'tool changed ({baseline["tool"]} -> {current["tool"]}): commit a new baseline '
                f'with owner approval; this is not a worsening']
    errors = []
    for unit, metrics in sorted(current['units'].items()):
        old = baseline['units'].get(unit)
        for metric, limit in limits.items():
            value = metrics.get(metric)
            if value is None:
                continue
            if old is None and value > limit:
                errors.append(f'{unit}: new unit {metric} {value} > limit {limit}')
            elif old is not None and old.get(metric) is not None and value > old[metric]:
                errors.append(f'{unit}: {metric} worsened {old[metric]} -> {value}')
    avg_now, avg_base = average_crap(current['units']), average_crap(baseline['units'])
    if avg_now >= crap_avg and avg_now > avg_base:
        errors.append(f'average CRAP {avg_now:.2f} >= {crap_avg} and worse than baseline {avg_base:.2f}')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('current', type=Path)
    parser.add_argument('--limits', type=Path, help='JSON object overriding the approved per-unit limits')
    args = parser.parse_args(argv)
    try:
        limits = dict(LIMITS, **(json.loads(args.limits.read_text()) if args.limits else {}))
        errors = compare(load(args.baseline), load(args.current), limits)
    except (OSError, ValueError) as exc:
        print(f'INPUT ERROR: {exc}', file=sys.stderr)
        return 2
    for error in errors:
        print(f'FAIL: {error}', file=sys.stderr)
    if not errors:
        print('PASS: no new or worsened violations')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
