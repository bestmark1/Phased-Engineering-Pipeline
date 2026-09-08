# Gate policy — one completion contract

This policy is shared by coordinator, Developer, Consistency, reviewers and QA.
It does not select models or alter configured agent roles.

## Permissions

- Inspect branch, status, relevant remotes and existing decisions before edits. Preserve
  unrelated uncommitted work. Disjoint work may proceed; overlap requires an owner decision.
- Never stash, overwrite other work, amend or rewrite history without explicit permission.
- A task/plan/DoD naming commit, push, PR, deploy, send, purchase or destructive data work
  does not grant permission. The owner's explicit request may grant it; do not ask again
  when that exact action and scope were already authorized. Record the authorization.
- Stage only owned paths/hunks. Commit only when authorized. Push/PR/deploy need their own
  explicit authorization; local delivery is a valid endpoint. Do not escalate permissions
  or bypass a denied hook to make a gate green. Do not expose secrets in evidence.
- Use disposable targets for destructive tests. Production data mutation needs separate
  explicit authorization and recovery planning, not a generic testing instruction.

## Risk depth and mandatory gates

Impact wins over file category. Auth, money, secrets, data migration/deletion, externally
consumed contracts and constitution-critical paths are High even if the diff is config
or a dependency bump. DEFAULT_REVIEW_DEPTH is a floor, never a ceiling.

| Depth | Before completion of an implementation slice |
|---|---|
| Low | Applicable deterministic checks, one independent combined SOLID/SRE review, targeted verification of changed behavior |
| Medium | Checks, advisory subtraction pass, recheck accepted edits, independent combined SOLID/SRE review, runtime slice check |
| High | Checks, subtraction and recheck, separate independent SOLID and SRE reviews, phase QA of critical paths including applicable recovery checks, explicit owner diff approval |

Retain final clean-checkout QA in all modes. A non-runtime docs/contract phase may use
its planned static/contract check with a reason; this cannot replace final runtime QA
for an executable product. Subtraction is advice, not a required removal quota.

Before work, the approved plan/phase registry names required gate IDs, kinds and expected
evidence. Product completion needs owner approval and product consistency; architecture
needs owner approval (or documented reuse); plan completion needs owner approval and full
consistency. These approvals are never inferred from a file's existence. Unchanged Lite
artifacts can reuse recorded approvals after validating continued applicability.
Coordinator initializes state, gathers role evidence and alone marks Done. A ready
artifact or Developer self-review leaves the row In Progress. No required gate can be
omitted because it did not run; use UNKNOWN and explain the missing evidence.

## Checks, STRICT_MODE and baseline failures

- Required build/setup/check failures block before substantive review. A missing check is
  UNKNOWN, not success. Mark a check n/a in the plan only if genuinely inapplicable.
- Brownfield test exceptions need a baseline snapshot, exact test identities **and failure
  signatures**, comparable environment/command evidence, bounded scope and explicit owner
  agreement made before accepting the gate. Counts alone are never enough: one old failure
  fixed plus one new failure introduced is still a regression.
- A current failure set must be a nonempty subset of the approved baseline set. Keep the
  nonzero exit and FAIL status in the command record. The receipt may be accepted **with
  exception**, not described as all-green. Exceptions cannot waive build/setup failures,
  missing execution, security gates, or active AC/QR acceptance failures.
- STRICT_MODE=true: blocking and major review findings prevent completion; minor findings
  are advisory. false: only noncritical major findings become advisory. Any safety,
  permission, required-check or active AC/QR failure must be classified blocking in both
  modes. Required UNKNOWN prevents completion in both modes. No mode invents PASS.
- Before Done, compare receipt gates against the approved plan, then run validate_gate.py.
  This is a local validation command, not an installed hook or automatic workflow engine.
  It validates declared records only: it cannot prove that evidence is truthful, that an
  owner really approved, that the plan is complete or that the supplied snapshot is current.

## Shared result envelope

All reviewers, QA and Consistency emit one envelope, including on success. The same
record shape is embedded in the receipt. Human-readable reports may accompany it.

```json
{
  "id": "solid",
  "kind": "review",
  "snapshot": "immutable artifact-set identifier",
  "status": "PASS",
  "evidence": "path to inspected diff and check report",
  "rubric_version": "solid-v2",
  "findings": []
}
```

A finding contains `criterion`, `status` (FAIL or UNKNOWN), `severity` (blocking,
major, minor), `evidence` and `fix`. FAIL needs a concrete location/observation and a
failure mechanism. For UNKNOWN, evidence names the missing context; fix names the check
that would settle it. n/a items belong in the accompanying report with a reason.

Aggregate review status: any blocking FAIL, or major FAIL in strict mode → FAIL;
otherwise any UNKNOWN → UNKNOWN; otherwise PASS (advisory findings remain visible).
A blocked review also uses this envelope, with a blocking prerequisite finding; it
must not claim that substantive review happened. The coordinator validates that safety
and acceptance findings were not misclassified as advisory.

Command records use kind `command`, `command`, integer `exit_code`, `status`, `evidence`
and `failures` (exact test-ID + failure-signature strings, empty for success). Only a
recorded exit 0 is PASS. An unrun command has status UNKNOWN and null exit_code.
Approval records use kind `approval`, `status`, `decision` (`approved`, `reused`, or
`unapproved`) and `evidence` pointing to explicit owner approval/reuse provenance.
Every record has id and snapshot. Bind receipts to the reviewed artifact snapshot;
changed code/config/prompts invalidate dependent evidence. An approval's evidence may
refer to an earlier decision when reuse was explicitly checked for this snapshot.

## Receipt (minimal complete example)

A real phase includes **all** gates from its approved plan, not just this small example.
Snapshot means an exact commit for final QA; before commit it may be a recorded hash
manifest of the relevant tracked and untracked artifacts, with provenance in evidence.
Do not include the receipt itself in its input snapshot (that creates a circular hash).

```json
{
  "schema_version": 1,
  "phase": "3.1",
  "snapshot": "fixture-commit",
  "strict_mode": true,
  "required_gates": ["tests", "solid"],
  "gates": [
    {"id":"tests", "kind":"command", "snapshot":"fixture-commit", "status":"PASS",
     "evidence":"reports/tests.txt", "command":"python3 -m unittest", "exit_code":0, "failures":[]},
    {"id":"solid", "kind":"review", "snapshot":"fixture-commit", "status":"PASS",
     "evidence":"reports/review.md", "rubric_version":"solid-v2", "findings":[]}
  ]
}
```

For an explicitly accepted legacy test failure only, add `baseline_exception` to its
command record: `baseline_snapshot`, `scope`, `approval`, `evidence`, `failures` (the
approved baseline ID/signature strings) and `test_only: true`. Keep current `failures`
in the command record. No exception applies to a review or approval gate.

Run `python3 <skill-root>/scripts/validate_gate.py receipt.json`. Exit 0 means the
supplied receipt is eligible (possibly with an explicitly reported baseline exception),
exit 1 means blocked/invalid, exit 2 means unreadable input or invalid CLI usage. It
executes no commands and never edits PROGRESS.md. The coordinator still checks actual
outputs, snapshot freshness, plan coverage, severity and authorization provenance.
