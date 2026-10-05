---
name: new-product-pipeline
description: >
  Plan and deliver a new product, or continue one this pipeline already runs, through product
  framing, architecture, vertical slices, independent review and QA. Use for an empty repository
  or a project whose pipeline artifacts (PRD, plan, PROGRESS) are current. For someone else's
  code, older code built outside this pipeline or a project with stale artifacts, use
  existing-system-pipeline. Not for isolated bugs, small edits or ordinary codebase questions.
---

# New Product Pipeline

Product framing, architecture, vertical slices, independent review and reproducible QA.
Keep the specialized roles and approval gates; load each role's reference only when it runs.
This skill does not select or change models. It does not authorize publication or deployment.

At the start of every run, load `references/pipeline-core.md`: principles, configuration,
artifacts, role prompts, gates and handoff shared with existing-system-pipeline.

## Which pipeline

| Situation | Pipeline |
|---|---|
| Empty repository / no product code yet | this skill (Full) |
| Project run by this pipeline, approved artifacts current | this skill (Lite) |
| Someone else's code; own code built outside this pipeline; stale or missing artifacts | existing-system-pipeline |
| Unclear | ask the owner one question with a recommendation |

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
- **Lite:** bounded initiative or improvement with established framing. Read existing
  approved artifacts, record what remains valid, and write only the initiative's delta.
  Reuse unchanged product/architecture decisions and their recorded approvals. Do not
  regenerate a constitution, diagrams or whole-product PRD merely to fill a template.
  The plan still states affected criteria, regressions to preserve and verification.

Both modes retain the logical stages, independent consistency checks and applicable
approvals. Reuse is not silent skipping: record the artifact/decision and why it still
applies. Unresolved or changed behavior, cost, contracts or permissions needs approval.
A standalone bugfix or minor edit does not need this pipeline at all.
