---
name: new-product-pipeline
description: >
  Plan and deliver a new product, or continue one this pipeline already runs, through product
  framing, architecture, vertical slices, independent review and QA. Use for an empty repository,
  a project this pipeline started that has not yet accepted a snapshot with executable specs, or
  one whose last accepted snapshot has a green specs job. For someone else's code, code built
  outside this pipeline without executable specs, or a stale project (specs job missing or red
  on the last accepted snapshot), use existing-system-pipeline. Not for isolated bugs, small
  edits or ordinary codebase questions.
---

# New Product Pipeline

Product framing, architecture, vertical slices, independent review and reproducible QA.
Keep the specialized roles and approval gates; load each role's reference only when it runs.
This skill does not select or change models. It does not authorize publication or deployment.

At the start of every run, load `references/pipeline-core.md`: principles, configuration,
artifacts, role prompts, gates and handoff shared with existing-system-pipeline.
Architect, Tech Lead and reviewers also load `references/quality-profile.md` (default quality
limits, which gate applies at which depth, ratchet, observability decision). CI is set up in
the first slice. Any role that creates, reads or checks `specs/INDEX.md` or `specs/` loads
`references/specs-contract.md` (requirement source, `specs` job, labels, black-box rules).

## Which pipeline

| Situation | Pipeline |
|---|---|
| Empty repository / no product code yet | this skill (bootstrap) |
| Started by new-product-pipeline, no accepted snapshot with a green `specs` job yet (bootstrap / MVP in progress) | this skill |
| Run by new-product-pipeline; last accepted snapshot has a green `specs` job (CI or local evidence) | this skill |
| Someone else's code; own code built outside new-product-pipeline (including the former single pipeline) without executable specs | existing-system-pipeline |
| A new-product project that is **stale** (below) | existing-system-pipeline |
| Unclear | ask the owner one question with a recommendation |

**Stale** applies only after a project has had an accepted snapshot with a green `specs` job,
and is judged on the last *accepted* snapshot, never on a red working commit: the `specs` job
missing, disabled or red there, or the owner declares it. Back to new-product-pipeline after an
existing-system run restored `specs` to green on an accepted snapshot and updated
`specs/INDEX.md`. The `specs` job is defined in `references/specs-contract.md`.

## Flow

```text
coordinator: inspect working tree, choose mode, initialize PROGRESS.md once
Product: discovery interview if the brief is raw → create or validate/reuse Narrative + PRD (+ MRD in Full)
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
must preserve the starting state.

## Modes and reuse

- **Full:** new product or unresolved market/positioning decisions. Narrative + MRD + PRD,
  then architecture, plan, slices, independent review and final QA.
- **MVP vs after-MVP:** until the first Released the PRD is the source of AC/QR; from then on
  `specs/INDEX.md` is, and changes flow BACKLOG.md → change (Lite) → specs
  (`references/specs-contract.md`).
- **Lite:** bounded initiative or improvement with established framing. Read existing
  approved artifacts, record what remains valid, and write only the initiative's delta.
  Reuse unchanged product/architecture decisions and their recorded approvals. Do not
  regenerate a constitution, diagrams or whole-product PRD merely to fill a template.
  The plan still states affected criteria, regressions to preserve and verification.

Both modes retain the logical stages, independent consistency checks and applicable
approvals. Reuse is not silent skipping: record the artifact/decision and why it still
applies. Unresolved or changed behavior, cost, contracts or permissions needs approval.
A standalone bugfix or minor edit does not need this pipeline at all.
