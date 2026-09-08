---
name: phased-engineering-pipeline
description: >
  Plan and deliver a full system or substantial end-to-end feature through product,
  architecture, implementation phases, independent review and QA. Use for an explicit
  phased pipeline or a multi-stage initiative, including unfamiliar existing codebases.
  Not for isolated bugs, small edits or ordinary codebase questions.
---

# Phased Engineering Pipeline

Product framing, architecture, vertical slices, independent review and reproducible QA.
Keep the specialized roles and approval gates; load each role's reference only when it runs.
This skill does not select or change models. It does not authorize publication or deployment.

## Flow

```text
coordinator: inspect working tree, choose mode, initialize PROGRESS.md once
brownfield only: Archaeology (source read-only) → report → READ-ONLY COMPLETE
Product: create or validate/reuse Narrative + PRD (+ MRD in Full)
  → OWNER APPROVAL of new/materially changed product decisions
Consistency (product) → resolve findings → gate accepted
Architect: create or validate/reuse architecture, constitution and project map
  → OWNER APPROVAL of new/materially changed architectural decisions
Tech Lead: create or update phase plan → OWNER APPROVAL of the execution plan
Consistency (full) → gate accepted
for each active implementation slice:
  Developer → self-check → ready for review (NOT Done)
  deterministic checks → subtraction pass at Medium/High → re-check accepted edits
  independent reviewer(s) and phase QA according to risk
  findings → targeted repair → checks + review of fixes and their affected behavior
  coordinator validates gate receipt → Done → next slice
QA: clean checkout of exact commit → release readiness + active AC/QR evidence
  → QA PASS, or FAIL/UNKNOWN with evidence; never silently waive gaps
Retro: minimal documentation improvements, no product edits
local handoff is a valid endpoint
push / PR / deploy only when explicitly authorized for those actions
```

For every commit shown or implied by a role, first apply `references/gate-policy.md`.
A dirty working tree is not permission to stash or overwrite other work. Branch creation
must preserve the starting state; do not create the same branch twice in brownfield mode.

## Core principles

- Repository artifacts carry decisions; PROGRESS.md carries state; HANDOFF.md carries
  what another session needs. Do not equate an artifact's existence with approval.
- Build vertical slices with a user-visible result. Phase isolation concerns intent,
  not a rigid file whitelist; necessary helpers/lockfiles are allowed within that intent.
  Never pull in future capabilities. Record deferred work with its target phase and reason.
- A test names the requirement, architectural constraint or regression it protects.
  Thorough internal coverage is welcome; tests without a purpose are findings, not a
  reason to silently delete them. Raise missing requirements rather than invent behavior.
- Preserve AC/QR IDs from PRD through architecture, plan, tests and QA. Never renumber or
  reuse retired IDs. See `references/artifact-changes.md` before changing approved artifacts.
- Implement the active slice in full, without speculative abstractions or recovery
  mechanisms. Real data, external inputs/calls and security boundaries retain rigor.
- Document project-specific surprises, not general framework tutorials. Capture debt
  explicitly; create documentation directories only when their first file is needed.
- Evidence must match the claim: run the product for user-visible behavior; use appropriate
  executable/static/contract checks for internal invariants. Green tests do not invalidate
  a concrete counterexample outside their coverage. No evidence means UNKNOWN, not PASS.
- The author does not perform independent acceptance of their own work. Deterministic
  checks precede reviewers; reviewers diagnose only what those checks do not establish.

## Modes and reuse

- **Full:** new product or unresolved market/positioning decisions. Narrative + MRD + PRD,
  then architecture, plan, slices, independent review and final QA.
- **Lite:** bounded initiative or improvement with established framing. Read existing
  approved artifacts, record what remains valid, and write only the initiative's delta.
  Reuse unchanged product/architecture decisions and their recorded approvals. Do not
  regenerate a constitution, diagrams or whole-product PRD merely to fill a template.
  The plan still states affected criteria, regressions to preserve and verification.
- **Brownfield:** map an unfamiliar existing system once per initiative before changing it,
  then use Lite. Archaeology is source read-only; refresh after material repository drift.
  No application test/config/schema changes belong in that pass. Its minimum regression
  harness becomes the first work of the first slice touching the relevant behavior.

All modes retain the logical stages, independent consistency checks and applicable
approvals. Reuse is not silent skipping: record the artifact/decision and why it still
applies. Unresolved or changed behavior, cost, contracts or permissions needs approval.
A standalone bugfix or minor edit does not need this pipeline at all.

### Brownfield baseline

Record the baseline SHA, test identities and failure signatures, not only failure counts.
A pre-existing red test is not automatically this initiative's defect, but a newly red
one is a regression. Any baseline exception must be explicitly agreed and recorded with
its scope; syntax/build/setup failures preventing useful verification remain blockers.
Apply `references/gate-policy.md` consistently in Developer, reviewers and QA.

Legacy test traceability is debt, not a blocking orphan list. This applies only to tests
at the recorded baseline. A test edited or used as evidence now must name its purpose.
Describe existing rules before desired rules in the brownfield constitution; a desired
constraint widely violated today is a finding, not permission for a sweeping rewrite.

## Configuration

Resolve project settings from the repository and approved decisions before the phase that needs them. Role-specific inputs and their sources are in `references/role-inputs.md`; they are not extra user questions.

| Placeholder | Description | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | Project name | Weather Tracker |
| `{{PIPELINE_MODE}}` | `lite`, `full`, or `brownfield` | `full` |
| `{{CHANGE_TARGET}}` | Brownfield only — the behavior the initiative will alter | tenant onboarding flow |
| `{{TECH_STACK}}` | Runtime + language + frameworks | Node.js, TypeScript strict, Next.js |
| `{{BUILD_COMMAND}}` | Build verification | `npm run build` |
| `{{RUN_COMMAND}}` | Start the product the way a user reaches it | `npm run dev` |
| `{{TEST_COMMAND}}` | Test runner | `npm test` |
| `{{LINT_COMMAND}}` | Linter / static analysis | `npm run lint` |
| `{{TYPECHECK_COMMAND}}` | Type checker if separate | `tsc --noEmit` |
| `{{QUALITY_RULES}}` | Stack-specific quality rules | strict TS, no secret logging |
| `{{INTERFACE_STYLE}}` | Contract style | TypeScript interfaces |
| `{{DOCS_URL}}` | Official docs URL | `https://nextjs.org/docs` |
| `{{ROLLBACK_COMMAND}}` | Code rollback only; data restoration requires its own tested procedure | `git revert HEAD` |
| `{{STRICT_MODE}}` | Noncritical major findings block when `true`; `false` makes only those advisory. Safety, required checks, approvals and UNKNOWN are never bypassed | `true` |
| `{{EVAL_COMMAND}}` | Eval suite for LLM behavior; empty only when no LLM behavior is in scope; otherwise record eval setup as pending | `npx promptfoo eval` |
| `{{DEFAULT_REVIEW_DEPTH}}` | `low`, `medium`, or `high` — floor for this project | `medium` |


## Artifacts and ownership

The coordinator initializes PROGRESS.md from `references/progress-template.md` before
Product (and before optional research), preserving any existing state. Roles report
outputs and evidence; only the coordinator closes a phase after required gates.
HANDOFF.md records readiness, blockers, approvals, baseline exceptions and next work.

```text
PROJECT_INDEX.md                  navigation
AGENTS.md                        preserve existing content; add missing map answers only
PROGRESS.md / HANDOFF.md          state / continuation evidence
SPEC_PLAN/
  archaeology-report.md          brownfield only
  Narrative.md / PRD.md           product framing (may reuse in Lite)
  MRD.md                         Full only
  clarification-report.md        product consistency
  ARCHITECTURE.md / CONSTITUTION.md
  IMPLEMENTATION_PLAN.md / phase-registry.md
  cross-artifact-analysis.md      full consistency
  EVAL_PLAN.md                    LLM behavior only
  gates/                         JSON gate receipts and referenced review evidence
```

`references/docs-scaffold.md` defines docs/; do not duplicate that tree elsewhere.
Every implementation phase names: purpose, scope, observable outcome, expected files,
dependencies, DoD, required checks, review depth, approvals and rollback/recovery evidence.

AGENTS.md answers five questions: project purpose, doc navigation, how to run, related
repos (if any), and what needs permission. The ≤60-line cap applies only to pipeline-owned
additions. Read existing content; preserve it and all `<!-- BEGIN:... -->` blocks.
Do not trim somebody else's rules to make room. Link long explanations into docs/.

## Role → prompt file

Every role in the flow has a prompt file. A role with no prompt file is a gap in the
skill, not a role the agent should improvise.

| Phase | Role | Prompt file | When |
|---|------|-------------|------|
| 0a | Archaeology | `references/archaeology-prompt.md` | brownfield only — read-only, once per initiative |
| 0 | Product | `references/product-prompt.md` | always — creates or validates/reuses approved framing |
| — | Domain Analyst | `references/analyst-prompt.md` | when domain research is needed |
| 0c | Consistency (`product`) | `references/consistency-prompt.md` | after product approval |
| 1 | Architect | `references/architect-prompt.md` | always — may reuse unchanged approved decisions |
| 2 | Tech Lead | `references/tech-lead-prompt.md` | always — may reuse unchanged approved decisions |
| 2a | Consistency (`full`) | `references/consistency-prompt.md` | after the plan |
| 3 | Developer | `references/developer-prompt.md` | per slice |
| 3r | Reviewer SOLID | `references/reviewer-solid-prompt.md` | per review depth |
| 3r | Reviewer SRE | `references/reviewer-sre-prompt.md` | High depth, or Medium when combined |
| 4 | QA & Release | `references/qa-prompt.md` | always — criteria exercised in a clean checkout |
| 5 | Retro | `references/retro-prompt.md` | after QA PASS, advisory |

`references/docs-scaffold.md` is not a role — it is the canonical `docs/` tree definition.
`references/piecemeal-growth.md` is not a role either — it is a review mode loaded for the
subtraction pass and unloaded afterwards.


## Gates, verdicts and completion

Before a gate, load `references/gate-policy.md`. It is the single policy for risk depth,
STRICT_MODE, baseline exceptions, permissions and eligibility for Done. Role prompts do
not invent alternatives. Reviews share the JSON envelope in that reference; Markdown
reports can accompany it but do not replace a verdict.

Before dispatch, resolve the inputs described in `references/role-inputs.md`. Do not send
unresolved placeholders; read the approved artifacts rather than ask the owner to retype them.

Before marking a phase Done, the coordinator compares the receipt's required gates to the
approved plan and runs the local validator (Python 3, no dependencies):

```bash
python3 <skill-root>/scripts/validate_gate.py <project>/SPEC_PLAN/gates/<phase>.json
```

Exit 0 means the supplied receipt permits completion; nonzero means malformed/incomplete
records, blocked checks or unresolved review/approval. This validates declared evidence,
not the truth of a model's claims or the completeness of an invented plan. The coordinator
must inspect the real artifacts/outputs. It neither changes PROGRESS.md nor executes commands.

### Repair and subtraction

A failed review triggers a targeted repair, not reimplementation. Re-run applicable checks;
review previously failing criteria AND behavior the fix could regress. Stop after repeated
failures on the same issue and reconsider the requirement, finding and root cause.
Do not run reviewers repeatedly until one agrees. Escalate substantive uncertainty to an
independent review and then the owner; unresolved blocking UNKNOWN cannot become Done.

At Medium/High depth, after checks pass, load `references/piecemeal-growth.md` for one
advisory KEEP/REMOVE/QUESTION pass. Developer applies only accepted, grounded findings,
then rechecks before independent review. No commit/amend is a prerequisite. A removal
that changes an approved artifact follows `references/artifact-changes.md`.

### LLM behavior

If behavior in scope depends on an LLM, load `references/eval-hooks.md` even if EVAL_COMMAND
is not configured yet. Pending eval setup is not evidence that the product has no LLM.
No model behavior in scope: record n/a. Otherwise plan the eval before the dependent phase.
Do not design a new metrics framework here; use suitable existing project tooling.

### Release and retro

Final QA uses an isolated checkout of the recorded commit, not a copy of the dirty working
tree. Provision disposable dependencies and explicitly provided test configuration; never
reuse production credentials/data for mutation. Acceptance criteria need runtime evidence;
QRs may use the appropriate static, contract or runtime check specified in the plan.
QA verifies and reports, never ships. If a commit is needed but not authorized, ask once;
report release verification pending rather than silently committing to satisfy the workflow.

After accepted QA, Retro may improve pointers/docs but not code or approved requirements.
If that changes startup instructions or executable commands, recheck the affected behavior
and refresh the reviewed snapshot before claiming release readiness.

### Session handoff

- Keep active work In Progress until its gates are accepted; explain ready-for-review,
  blocked or UNKNOWN in HANDOFF.md. Do not let the next session infer acceptance from files.
- Update PROGRESS/HANDOFF, relevant debt and surprises; record the next bounded step.
- Report observed checks, assumptions, gaps and risks. Record available run telemetry via
  `references/run-economics.md`; unavailable metrics stay unavailable, explicit budgets apply.
- Stage/commit only authorized own changes; push/PR are optional, separately authorized.
