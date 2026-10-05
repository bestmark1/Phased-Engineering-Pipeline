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
- **Status** `active` or `retired`.
- **Behavior** the full normative statement, not a summary. A `spec`-verified row states
  When and Then (Given when there is a precondition); error conditions stay in the row.
- **Verify** `spec` (executable spec), `static`, `contract` or `eval`. Non-`spec` rows name
  their check in **Evidence** (command or rule and scope).
- **Origin** `PRD`, `delta`, `OBS`, or `deviation:OBS-n` (an approved change of observed behavior).

## Executable specs

- Given-When-Then, written in the project's existing test framework — no Cucumber or other
  new dependency. Specs live under `specs/`; shared helpers only under `specs/support/`.
- **Label:** each spec carries its requirement as a quoted string literal `"req:AC-001"` in a
  test name, tag, marker or parameter (e.g. `@pytest.mark.req("req:AC-001")`,
  `test("req:AC-001 shows name", …)`). A mention in a comment or unquoted text is not a label.
- **Black box:** `specs/**` → `specs/support/**` → the product's public entry points only
  (HTTP, UI driver, CLI, published SDK). Neither imports internal product modules; enforce
  with the stack's dependency linter (import-linter, dependency-cruiser or equivalent) as a
  required gate.
- **No mock of the system under test.** Allowed: state setup through a public entry point or
  a documented seed/fixture; simulators of external dependencies (payments, LLM, third-party
  APIs) listed in the plan.

## Three separate checks

1. Imports — the dependency linter (required gate).
2. Traceability — `python3 <skill-root>/scripts/check_index.py --index specs/INDEX.md --specs specs`
   (gate id `index-check`): every active `spec` row has a labeled spec; every label names an
   existing, non-retired ID; non-`spec` rows name their evidence.
3. Assertion strength — the test critic in review (Medium/High). Reject, for example:
   asserting status 200 without the body; asserting a value that comes from a mock; a spec
   without an observable Then.
