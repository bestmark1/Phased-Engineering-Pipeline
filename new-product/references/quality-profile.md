# Quality profile — default proposal for a new product

Loaded by the Architect (to propose) and by Tech Lead and reviewers (to apply). The profile is
a proposal: it binds only after the owner approves it in the architecture phase. It is then
recorded in the project's `QUALITY_COMMAND` configuration with tool versions pinned in the
lockfile. Generated and vendored code is excluded by an explicit list.

## Default limits

| Metric | Limit |
|---|---|
| Cyclomatic complexity per unit | ≤ 10 |
| Cognitive complexity per unit | ≤ 15 |
| CRAP per unit / average | max 30 / avg < 5 |
| Dependency cycles | 0 |
| Dead code | 0, with an exceptions file where every entry states its reason |
| Diff coverage (changed lines) | ≥ 80% |

Pick the stack's established tools (e.g. TypeScript: ESLint + sonarjs, knip,
dependency-cruiser, Stryker, fast-check; Python: Ruff, Lizard, vulture, import-linter,
mutmut, Hypothesis). A metric the stack cannot measure is decided by the owner before the
plan: replace the tool or drop the metric from the profile — never silently.

## Which gate applies

| Gate | Low | Medium | High | No tool for the stack |
|---|---|---|---|---|
| Complexity, CRAP, cycles, dead code | required | required | required | owner decides before the plan |
| Diff coverage ≥ 80% | advisory | required + test critic | required + test critic | owner decides before the plan |
| Mutation testing on the diff | — | advisory | required | `n/a + reason` in the plan |
| Property-based tests | — | advisory | required for pure functions with invariants | `n/a + reason` |

The test critic is an item of the reviewer's rubric at Medium/High, not a new role: it checks
that tests would fail if the traced behavior broke (see `references/specs-contract.md`,
assertion strength). Coverage without the critic or mutation is a number, not evidence.
Mutation jobs run in CI only at High (CI minutes).

## Ratchet

- **New units** (a function/module absent from the committed baseline) meet the absolute
  limits above.
- **Existing units** must not get worse than the baseline; improving a unit that is still
  above the limit passes (complexity 20 → 18 = PASS; a new unit at 12 = FAIL).
- A metric absent from a unit's baseline (e.g. re-enabled after being dropped) meets the
  absolute limit.
- The baseline is always read from the base commit, never regenerated in the working tree:
  `git show <base>:<baseline path> > baseline.json`. A new tool or tool version is a new
  baseline: a separate commit with an owner approval gate, not counted as a worsening.

Every unit reports every metric of the approved profile; a missing measurement fails, it is
never a pass. A metric the owner dropped from the profile is passed as `null` in `--limits`.
Feed the per-unit metrics exported by the project's tools to
`python3 <skill-root>/scripts/quality_ratchet.py baseline.json current.json` (format in the
script's help); it is the required `quality` gate described in `references/gate-policy.md`.

## Observability decision (Architect, ADR)

Always: structured events with request and entity IDs — a QR stating that an agent answers
"what happened to X" with one query. A full event store with snapshots when **two or more**
hold: history/audit matters (money, orders, statuses); "how did we reach this state" is a
real question; behavior spans several services; the product has an LLM part (events feed
evals and simulations). Record the decision in an ADR; the owner approves it.

CI is set up in the first slice (default GitHub Actions) with the same entry point the local
fallback uses.
