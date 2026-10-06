---
name: existing-system-pipeline
description: >
  Enter and change an existing system safely: read-only archaeology and an exact test baseline
  first, then product delta, architecture, vertical slices, independent review and QA. Use for
  someone else's code, code built outside new-product-pipeline without executable specs, or a
  stale new-product project (specs job missing or red on the last accepted snapshot). For an
  empty repository, a project new-product-pipeline started, or one whose last accepted snapshot
  has a green specs job, use new-product-pipeline. Not for isolated bugs, small edits or
  ordinary codebase questions.
---

# Existing System Pipeline

Map an unfamiliar system before changing it, then deliver a bounded delta with the same roles,
approval gates, independent review and reproducible QA as new-product-pipeline.
This skill does not select or change models. It does not authorize publication or deployment.

At the start of every run, load `references/pipeline-core.md`: principles, configuration,
artifacts, role prompts, gates and handoff shared with new-product-pipeline.

## Which pipeline

| Situation | Pipeline |
|---|---|
| Empty repository / no product code yet | new-product-pipeline (bootstrap) |
| Started by new-product-pipeline, no accepted snapshot with a green `specs` job yet (bootstrap / MVP in progress) | new-product-pipeline |
| Run by new-product-pipeline; last accepted snapshot has a green `specs` job (CI or local evidence) | new-product-pipeline |
| Someone else's code; own code built outside new-product-pipeline (including the former single pipeline) without executable specs | this skill |
| A new-product project that is **stale** (below) | this skill |
| Unclear | ask the owner one question with a recommendation |

The owner's declaration that a project is stale moves it to existing-system-pipeline at any
time and takes precedence over every row above, bootstrap included. Otherwise **stale** applies
only after a project has had an accepted snapshot with a green `specs` job, and is judged on the
last *accepted* snapshot, never on a red working commit: the `specs` job missing, disabled or
red there. Back to new-product-pipeline after an
existing-system run restored `specs` to green on an accepted snapshot and updated
`specs/INDEX.md`. The `specs` job is defined in `references/specs-contract.md`.

## Flow

```text
coordinator: inspect working tree, initialize PROGRESS.md once
Archaeology (source read-only) → report → READ-ONLY COMPLETE
Product: create or validate/reuse the delta's Narrative + PRD
  → OWNER APPROVAL of new/materially changed product decisions
Consistency (product) → resolve findings → gate accepted
Architect: create or validate/reuse architecture, constitution and project map
  → OWNER APPROVAL of new/materially changed architectural decisions
Tech Lead: create or update phase plan → OWNER APPROVAL of the execution plan
Consistency (full) → gate accepted
for each active implementation slice (the first one starts with the regression harness):
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
must preserve the starting state; do not create the same branch twice.

| Phase | Role | Prompt file | When |
|---|------|-------------|------|
| 0a | Archaeology | `references/archaeology-prompt.md` | read-only, once per initiative |

The remaining roles are listed in `references/pipeline-core.md`.
Requirements live in `specs/INDEX.md` from the Product delta on; any role that creates, reads
or checks `specs/INDEX.md` or `specs/` loads `references/specs-contract.md`.

## Mode

Map an unfamiliar existing system once per initiative before changing it, then deliver as a
bounded delta: read existing approved artifacts, record what remains valid, write only the
initiative's delta. Archaeology is source read-only; refresh after material repository drift.
No application test/config/schema changes belong in that pass. Its minimum regression
harness becomes the first work of the first slice touching the relevant behavior.

All stages, independent consistency checks and applicable approvals are retained. Reuse is
not silent skipping: record the artifact/decision and why it still applies. Unresolved or
changed behavior, cost, contracts or permissions needs approval. A standalone bugfix or
minor edit does not need this pipeline at all.

### Baseline

Record the baseline SHA, test identities and failure signatures, not only failure counts.
A pre-existing red test is not automatically this initiative's defect, but a newly red
one is a regression. Any baseline exception must be explicitly agreed and recorded with
its scope; syntax/build/setup failures preventing useful verification remain blockers.
Apply `references/gate-policy.md` consistently in Developer, reviewers and QA.

Legacy test traceability is debt, not a blocking orphan list. This applies only to tests
at the recorded baseline. A test edited or used as evidence now must name its purpose.
Describe existing rules before desired rules in the constitution; a desired constraint
widely violated today is a finding, not permission for a sweeping rewrite.
