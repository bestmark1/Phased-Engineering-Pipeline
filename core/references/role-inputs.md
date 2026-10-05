# Role inputs — resolve before dispatch

The SKILL.md configuration table lists project settings, not every prompt interpolation.
Read the approved request/artifacts and repository; do not interview the owner for values
already present. Substitute literal values before sending a role prompt. Missing material
input means stop that role and name the gap; do not let a placeholder act as a requirement.
Optional inputs get an explicit `none / not applicable: reason`, not fabricated content.

| Input | Source |
|---|---|
| CURRENT_DATE | Observed current date for the report, not a guessed placeholder |
| PROJECT_DESCRIPTION | Owner's request + approved Narrative/PRD; preserve the original request verbatim in a separate brief block |
| DOMAIN_RESEARCH | Existing research notes, or no research needed with reason |
| PRD_SUMMARY, PRD_CONTENT, PRD_ACCEPTANCE_CRITERIA | Approved PRD; summaries preserve active AC/QR IDs, constraints and non-goals; full document remains accessible |
| INTEGRATION_REQUIREMENTS, FUTURE_EXTENSIBILITY | Approved PRD + architecture decisions; no speculative extension points |
| TECH_STACK_DETAIL | Existing manifests/lockfiles + approved stack decisions |
| SYSTEM_COMPONENTS, CORE_INTERFACES | Existing architecture when available; otherwise scoped draft proposals from the Architect, not extra owner questionnaires |
| ARCHITECTURE_SUMMARY | Approved ARCHITECTURE.md + CONSTITUTION.md; full documents remain accessible |
| IMPLEMENTATION_PLAN | Approved full implementation plan |
| CURRENT_PHASE, PHASE_DESCRIPTION, PHASE_REQUIREMENTS, FILES_TO_CREATE | Active plan/phase-registry entry; expected files are not an intent whitelist |
| CODE_TO_REVIEW, IMPLEMENTED_FILES_LIST | Actual diff and changed-file inventory of the recorded snapshot, plus callers/shared utilities; not only Developer's report |
| CHECK_SCOPE | `product` or `full` from the flow |
| ARTIFACTS_CONTENT | Versioned input set appropriate for CHECK_SCOPE |
| PROJECT_NAME, PIPELINE_MODE, CHANGE_TARGET, TECH_STACK, QUALITY_RULES, INTERFACE_STYLE, DOCS_URL | Project settings in SKILL.md + approved decisions |
| BUILD_COMMAND, RUN_COMMAND, TEST_COMMAND, LINT_COMMAND, TYPECHECK_COMMAND, QUALITY_COMMAND, ROLLBACK_COMMAND, EVAL_COMMAND | Repository scripts/tooling and approved plan; no guessed commands; applicability/pending state follows gate-policy.md |
| STRICT_MODE, DEFAULT_REVIEW_DEPTH | Explicit project setting or documented defaults: true and medium |

`{{PLACEHOLDERS}}` in a preamble describes substitution, it is not a project variable.
Before dispatch, inspect the rendered brief for remaining `{{...}}` template tokens.
This final check is mechanical: `python3 <skill-root>/scripts/validate_gate.py --prompt brief.txt`.
A clean result proves only that tokens were resolved, not that the brief is complete.
The coordinator also attaches snapshot identity, required gates/check outputs, existing
approvals, exceptions and previous findings as context, without creating new configuration
questions. Never attach secrets. Reviewers receive evidence, not the author's model/identity.
