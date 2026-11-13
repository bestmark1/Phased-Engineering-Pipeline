# Receipt contract — receipts, CI provenance, release record

Coordinator-only companion of `references/gate-policy.md`: load it before writing or
validating a phase receipt or a release record. Gate policy stays the single source for
permissions, risk depth, STRICT_MODE and the result envelope; this file only fixes the
record layouts the validator reads.

## CI provenance

CI provenance: the CI job publishes a command-level artifact (`repository`, `workflow`,
`job`, `run_id`, `run_attempt`, `head_sha`, `commands: [{command, exit_code, failures,
skipped}]`). The coordinator downloads it for the exact run and attempt (`gh run download
<run_id>`; `gh run view <run_id> --attempt <n> --json headSha,conclusion,jobs` for the
summary) and runs the validator with `--ci-artifact`, once per job/attempt artifact when the receipt spans
several jobs (e.g. `tests` and `specs`); each record is matched to the artifact of its own run. A command the receipt declares but the
artifact lacks or marks skipped is not evidence. An approved legacy failure keeps its
nonzero exit in CI too; CI never turns an exception green.

## Receipt (minimal complete example)

A real phase includes **all** gates from its approved plan, not just this small example.
Snapshot means an exact commit for final QA; before commit it may be a recorded hash
manifest of the relevant tracked and untracked artifacts, with provenance in evidence.
Do not include the receipt itself in its input snapshot (that creates a circular hash).

```json
{
  "schema_version": 2,
  "phase": "3.1",
  "snapshot": "fixture-commit",
  "snapshot_kind": "commit",
  "scope": "slice",
  "strict_mode": true,
  "required_gates": ["tests", "solid"],
  "gates": [
    {"id":"tests", "kind":"command", "snapshot":"fixture-commit", "status":"PASS",
     "evidence":"reports/tests.txt", "command":"python3 -m unittest", "exit_code":0, "failures":[],
     "runner":"local", "local":{"command":"make ci", "worktree":"clean",
     "head_sha":"fixture-commit", "reason":"no CI configured"}},
    {"id":"solid", "kind":"review", "snapshot":"fixture-commit", "status":"PASS",
     "evidence":"reports/review.md", "rubric_version":"solid-v2", "findings":[]}
  ]
}
```

Receipt fields: `snapshot_kind` (`commit` or `manifest`), `scope` (`slice` or
`initiative`), optional `require_ci` (plan demands CI evidence), `index_present` (true once
`specs/INDEX.md` exists; then the `index-check` command gate is required in every receipt). An initiative receipt also
lists `active_criteria` (every active AC/QR ID) and contains `qa-blind` and `qa-internal`
review gates whose `coverage` lists the AC resp. QR they verified; missing coverage is
UNKNOWN. The initiative's `index-check` runs `check_index.py --final`, so no approved row is left
`planned`. A coverage entry is an ID verified on this snapshot, or after a repair a carried-over
record `{id, snapshot (earlier), applicability}` (`references/qa-prompt.md`). The validator accepts schema 2 only; receipts of phases accepted before the
split stay as history and are not revalidated.

For an explicitly accepted legacy test failure only, add `baseline_exception` to its
command record: `baseline_snapshot`, `scope`, `approval`, `evidence`, `failures` (the
approved baseline ID/signature strings) and `test_only: true`. Keep current `failures`
in the command record. No exception applies to a review or approval gate.

## Release record

Released is a separate state after initiative completion. The coordinator writes
`SPEC_PLAN/releases/<n>.json`: `done_snapshot`, `receipt` (path of the accepted initiative
receipt) and `receipt_sha256` (SHA-256 of that file, checked by the CLI), `deployed_sha` (must equal `done_snapshot`), optional `artifact_digest`,
`environment`, `authorization` (the owner's explicit deploy request), `first_release`
(boolean; when false, `previous_release` names the earlier release record) and `smoke`: the plan's approved checks, each `{id, criterion (AC/QR), status,
evidence}` with `criterion` an active AC/QR of the receipt. Released only when every smoke check is PASS; a generic health check is not a
smoke check. A first release needs a passing `index-check` command gate in the accepted receipt, so the
requirement registry existed before final QA (`references/specs-contract.md`). Validate with
`python3 <skill-root>/scripts/validate_gate.py --release SPEC_PLAN/releases/<n>.json <receipt>`.

Run `python3 <skill-root>/scripts/validate_gate.py receipt.json`. Exit 0 means the
supplied receipt is eligible (possibly with an explicitly reported baseline exception),
exit 1 means blocked/invalid, exit 2 means unreadable input or invalid CLI usage. It
executes no commands and never edits PROGRESS.md. The coordinator still checks actual
outputs, snapshot freshness, plan coverage, severity and authorization provenance.
