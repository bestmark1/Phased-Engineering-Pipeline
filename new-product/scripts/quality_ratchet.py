#!/usr/bin/env python3
"""Compare per-unit quality metrics with the committed baseline (references/quality-profile.md).

New units must meet absolute limits; existing units must not get worse; a different measuring
tool/version needs a new baseline commit. Input JSON: {"tool": "lizard 1.17.10",
"units": {"src/a.py::f": {"cyclomatic": 7, "cognitive": 9, "crap": 4.0}}}.
Exit 0 = pass, 1 = violations, 2 = bad input.
"""
import argparse
import json
import math
from pathlib import Path
import sys

LIMITS = {'cyclomatic': 10, 'cognitive': 15, 'crap': 30}
CRAP_AVG = 5


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def load(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('tool'), str) or not isinstance(data.get('units'), dict):
        raise ValueError(f'{path}: expected {{"tool": str, "units": {{...}}}}')
    for unit, metrics in data['units'].items():
        if not isinstance(metrics, dict) or not all(number(v) for v in metrics.values()):
            raise ValueError(f'{path}: {unit}: metrics must be an object of finite numbers')
    return data


def average_crap(units):
    values = [m['crap'] for m in units.values() if number(m.get('crap'))]
    return sum(values) / len(values) if values else 0.0


def compare(baseline, current, limits=LIMITS, crap_avg=CRAP_AVG):
    if baseline['tool'] != current['tool']:
        return [f'tool changed ({baseline["tool"]} -> {current["tool"]}): commit a new baseline '
                f'with owner approval; this is not a worsening']
    errors = []
    limits = {m: l for m, l in limits.items() if l is not None}  # null in --limits drops a metric
    for unit, metrics in sorted(current['units'].items()):
        old = baseline['units'].get(unit)
        for metric, limit in limits.items():
            value = metrics.get(metric)
            if value is None:
                errors.append(f'{unit}: {metric} not measured (a missing measurement is not a pass)')
                continue
            previous = None if old is None else old.get(metric)
            if previous is None and value > limit:  # new unit, or metric not in the baseline
                errors.append(f'{unit}: {"new unit " if old is None else "unbaselined "}{metric} {value} > limit {limit}')
            elif previous is not None and value > previous:
                errors.append(f'{unit}: {metric} worsened {old[metric]} -> {value}')
    if 'crap' not in limits:
        return errors
    # Baseline average over units still present, so deleting good units is not a worsening.
    kept = {u: m for u, m in baseline['units'].items() if u in current['units']}
    avg_now, avg_base = average_crap(current['units']), average_crap(kept)
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
        override = json.loads(args.limits.read_text()) if args.limits else {}
        if not isinstance(override, dict):
            raise ValueError('limits must be a JSON object')
        limits = dict(LIMITS, **override)
        if not all(v is None or number(v) for v in limits.values()):
            raise ValueError('limits must be numbers or null')
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
