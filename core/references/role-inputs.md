# Role inputs — resolve before dispatch

The configuration table in `references/pipeline-core.md` lists project settings, not every prompt interpolation.
Read the approved request/artifacts and repository; do not interview the owner for values
already present. Substitute literal values before sending a role prompt. Missing material
input means stop that role and name the gap; do not let a placeholder act as a requirement.
Optional inputs get an explicit `none / not applicable: reason`, not fabricated content.

| Input | Source |
|---|---|
| CURRENT_DATE | Observed current date for the report, not a guessed placeholder |
| PROJECT_DESCRIPTION | Owner's request + approved Narrative/PRD; preserve the original request verbatim in a separate brief block |
| DOMAIN_RESEARCH | Existing research notes, or no research needed with reason |
| PRD_SUMMARY, PRD_CONTENT | Approved PRD (in existing-system: the scenario's approved delta PRD — framing only, criteria live in INDEX); summaries preserve active AC/QR IDs, constraints and non-goals; full document remains accessible |
| PRD_ACCEPTANCE_CRITERIA | Active AC/QR from the requirement source in `references/specs-contract.md` (PRD only before a new product's first Released; otherwise `specs/INDEX.md`), retired rows excluded |
| ACTIVE_CRITERIA, active AC/QR (any role) | new-product: PRD until the first Released, then `specs/INDEX.md`; existing-system: `specs/INDEX.md` from the Product delta on, regardless of Released or PRD. See `references/specs-contract.md` |
| QA blind-pass inputs | Active AC, snapshot SHA, run instruction, test credentials/data only — no source, diff, reports, outputs or prior findings (`references/qa-prompt.md`) |
| INTEGRATION_REQUIREMENTS, FUTURE_EXTENSIBILITY | Approved PRD + architecture decisions; no speculative extension points |
| TECH_STACK_DETAIL | Existing manifests/lockfiles + approved stack decisions |
| SYSTEM_COMPONENTS, CORE_INTERFACES | Existing architecture when available; otherwise scoped draft proposals from the Architect, not extra owner questionnaires |
| ARCHITECTURE_SUMMARY | Approved ARCHITECTURE.md + CONSTITUTION.md; full documents remain accessible |
| IMPLEMENTATION_PLAN | Approved full implementation plan |
| CURRENT_PHASE, PHASE_DESCRIPTION, PHASE_REQUIREMENTS, FILES_TO_CREATE | Active plan/phase-registry entry; expected files are not an intent whitelist |
| CODE_TO_REVIEW, IMPLEMENTED_FILES_LIST | Actual diff and changed-file inventory of the recorded snapshot, plus callers/shared utilities; not only Developer's report |
| CHECK_SCOPE | `product` or `full` from the flow |
| ARTIFACTS_CONTENT | Versioned input set appropriate for CHECK_SCOPE |
| PROJECT_NAME, PIPELINE_MODE, CHANGE_TARGET, TECH_STACK, QUALITY_RULES, INTERFACE_STYLE, DOCS_URL | Project settings in `references/pipeline-core.md` + approved decisions |
| BUILD_COMMAND, RUN_COMMAND, TEST_COMMAND, LINT_COMMAND, TYPECHECK_COMMAND, QUALITY_COMMAND, ROLLBACK_COMMAND, EVAL_COMMAND | Repository scripts/tooling and approved plan; no guessed commands; applicability/pending state follows gate-policy.md |
| STRICT_MODE, DEFAULT_REVIEW_DEPTH | Explicit project setting or documented defaults: true and medium |
| REVIEW_DEPTH | This slice's depth from the approved plan/phase registry (never below DEFAULT_REVIEW_DEPTH); Low/Medium = one combined SOLID+SRE review |
| SPECS_DIR, STATE_FILE, INITIATIVE_DIR | Project settings (`references/pipeline-core.md`): where executable specs + INDEX, run state and initiative artifacts live |

The coordinator also attaches snapshot identity, required gates/check outputs, existing
approvals, exceptions and previous findings as context, without creating new configuration
questions. Never attach secrets. Reviewers receive evidence, not the author's model/identity.

## Pipeline context block — paste into every role brief

Role prompts are shared by both pipelines and do not know which one is running. A role agent
sees only its brief, so the coordinator appends this block, filled for the run, to every brief.
Without it a role follows generic defaults that contradict the pipeline (trial findings F5–F7,
seam audit G1–G19).

```text
PIPELINE CONTEXT (overrides the generic prompt where they differ)
- Pipeline: <new-product-pipeline: mode full|lite, MVP|after-MVP> | <existing-system-pipeline: step N of 0–8>.
  Phase/row numbers in the prompt that belong to the other pipeline (e.g. 0a, 0c, 2a) do not apply;
  state lives in <STATE_FILE>.
- Requirement source: <PRD | SPECS_DIR/INDEX.md> (references/specs-contract.md). Take AC/QR only from it.
  At initiative completion no row may remain planned (check_index --final).
  In existing-system the delta PRD is framing only; its stories need no AC of their own.
- INDEX statuses: active = needs its spec/evidence now; planned = spec arrives in a later slice (no spec yet,
  no label yet); retired = ignore. OBS-n rows = observed current behavior, a safety net, not a requirement:
  exclude them from QA criteria lists, coverage and blind-pass inputs; they change only through an owner
  OBS decision and the parity gate.
- Specs (SPECS_DIR): label = string literal starting with req:<ID> in a test name/tag/marker — never a comment
  or docstring; black box through public entry points; fakes only for external dependencies; run under the
  hermetic guard; a characterization spec never sets the value it characterizes.
- Gates of this slice/run: <ids from the approved plan, e.g. specs, index-check, parity, quality, review ids,
  approvals>; receipt schema 2 (references/gate-policy.md).
- This role may write: <exact paths>. docs/ writes need the step-0 permission (existing-system).
- Slices: existing-system slice 1 = characterization (OBS specs + parity baseline, no behavior change,
  exempt from the user-visible-outcome rule); every later slice touching the scenario carries `parity`.
- Pipeline-specific references this role must load (name them; P10): existing-system — the parity
  procedure and the entry OBS rules; new-product — the quality profile.
- Extra inputs: <archaeology report, transcripts for Retro, parity files, ...>.
```

Before dispatch, inspect the rendered brief for remaining template tokens. This final check is
mechanical: `python3 <skill-root>/scripts/validate_gate.py --prompt brief.txt`.
A clean result proves only that tokens were resolved, not that the brief is complete.
