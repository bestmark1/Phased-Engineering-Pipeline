# Specs contract — requirement registry and executable black-box specs

Load when a role creates, reads or checks `specs/INDEX.md` or anything under `specs/`, and
before the final QA that precedes a first release. Checked by `scripts/check_index.py`.

## Which document is the source of active AC/QR

| Pipeline | Source |
|---|---|
| new-product, before the first Released | PRD (as today; `references/artifact-changes.md` applies) |
| new-product, from the first Released on | `specs/INDEX.md`; the PRD text is frozen as history |
| existing-system | `specs/INDEX.md` from the Product delta on, regardless of Released or PRD |

new-product: before completing the initiative that leads to the first release, the
coordinator creates INDEX from the PRD's AC/QR (same IDs, retired kept), adds the
`index-check` gate to the initiative receipt and runs Consistency (`full`) on the transfer —
all before final QA, so INDEX is part of the accepted snapshot. existing-system: Product
creates INDEX with the delta; the owner approves it together with the delta. A project
migrated from the old single skill with a past release creates INDEX as the first step of
its next initiative. `references/artifact-changes.md` rules (never renumber, never reuse a
retired ID) apply to INDEX exactly as to the PRD.

## INDEX format

One Markdown table with exactly these columns:

| ID | Status | Behavior | Verify | Evidence | Origin |
|---|---|---|---|---|---|
| AC-001 | active | Given a registered user When they log in Then their name is shown | spec | | PRD |
| QR-001 | active | No secret value appears in logs | static | `make secrets-scan` | PRD |
| AC-002 | retired | Given … When … Then … | spec | | PRD |

- **ID** `AC-n`, `QR-n` or `OBS-n` (observed behavior, existing-system); unique.
- **Status** `active` (its spec/evidence must exist now), `planned` (approved, its spec arrives with
  the slice that implements it — no spec and no label yet), or `retired`. The implementing slice sets
  `planned` → `active` in the same commit as the spec, so `index-check` stays green on every receipt.
  Product writes new delta criteria as `planned`.
- **Behavior** the full normative statement, not a summary. A `spec`-verified row states
  When and Then (Given when there is a precondition); error conditions stay in the row.
- **Verify** `spec` (executable spec), `static`, `contract` or `eval`. Non-`spec` rows name
  their check in **Evidence** (command or rule and scope).
- **Origin** `PRD`, `delta`, `OBS`, or `deviation:OBS-n` (an approved change of observed behavior).

## Observed behavior (existing-system)

`OBS-n` rows record what an existing system does today, found by the characterization slice:
a protective safety net, not a requirement. The owner decides them per scenario in one batch
(existing-system's entry reference): intended → an `AC` with Origin `OBS`, applied at once;
must change → an `AC` with Origin `deviation:OBS-n`, applied by the slice that implements the
fix. Either way adding the AC, relabeling the spec and retiring the OBS row happen in one commit;
undecided OBS rows stay active. A changed behavior is accepted only through the
parity gate with an approved delta pointing to that deviation row.

## Executable specs

Paths below say `specs/`; read them as `{{SPECS_DIR}}` (`references/pipeline-core.md`) when the project
uses another directory.


- Given-When-Then, written in the project's existing test framework — no Cucumber or other
  new dependency. Specs live under `specs/`; shared helpers only under `specs/support/`.
- **Label:** each spec carries its requirement at the start of a string literal in code:
  `"req:AC-001"` alone or followed by a space, in a test name, tag, marker or parameter
  (e.g. `@pytest.mark.req("req:AC-001")`, `test("req:AC-001 shows name", …)`). The checker
  ignores `//`, `#`, `/* */` and `<!-- -->` comments, comment-only lines and text files
  (`.md`, `.txt`, `.rst`). It cannot recognize docstrings — reviewers reject a label there.
- **Black box:** `specs/**` → `specs/support/**` → the product's public entry points only
  (HTTP, UI driver, CLI, published SDK). Neither imports internal product modules; enforce
  with the stack's dependency linter (import-linter, dependency-cruiser or equivalent) as a
  required gate.
- **Hermetic guard (required).** The `specs` job runs every spec under a clean environment (only PATH,
  HOME, LANG, TZ and the run's own variables) and a guard that makes any socket connect, including
  loopback, and any spawn of network/model/remote tools (curl, ssh, docker, model CLIs) fail the run —
  even if the product swallows the error. Settings the specs need are set explicitly; nothing is read
  from the caller's shell or env files. A Python reference implementation ships as
  `scripts/hermetic_guard.py`; other stacks provide an equivalent. Without the guard a spec can reach a
  paid model or let the environment fake a parity result (trial finding F12).
- **A characterization spec never sets the value it characterizes.** Pinned settings, fixtures and
  fakes cover only the inputs and external dependencies of the Given; the observed value must come
  from the product's own defaults or code. Reviewer check: change that value in the product (in a
  scratch copy, under the guard) — the spec must fail (trial finding F14).
- **No mock of the system under test.** Allowed: state setup through a public entry point or
  a documented seed/fixture; simulators of external dependencies (payments, LLM, third-party
  APIs) listed in the plan.

## The `specs` job and the `index-check` gate

- **`specs` job** (CI, and the same entry point locally): runs every spec under `specs/`, the
  dependency linter for `specs/**`, and `check_index.py`. It is mandatory from the first slice
  that adds `specs/`. In new-product-pipeline the first slice that delivers a user-visible
  behavior adds it; until the first accepted snapshot with a green `specs` job the project is
  in bootstrap/MVP, not stale.
- **`index-check`**: once `specs/INDEX.md` exists in a snapshot, every receipt for that snapshot
  — slice and initiative — sets `index_present: true` and includes the `index-check` command
  gate. The validator rejects a receipt with `index_present: true` and no such gate.

Tests outside `specs/` (unit, integration) are not exempt from traceability: each still names
the requirement, architectural constraint or regression it protects (core principles in
`references/pipeline-core.md`). Moving a test out of `specs/` to avoid an AC is not allowed; a
behavior worth testing with no requirement behind it goes to the owner as a candidate AC.

## Three separate checks

1. Imports — the dependency linter (required gate).
2. Traceability — `python3 <skill-root>/scripts/check_index.py --index specs/INDEX.md --specs specs`
   (gate id `index-check`): every active `spec` row has a labeled spec; every label names an
   existing, non-retired ID; non-`spec` rows name their evidence.
3. Assertion strength — the test critic in review (Medium/High). Reject, for example:
   asserting status 200 without the body; asserting a value that comes from a mock; a spec
   without an observable Then.
