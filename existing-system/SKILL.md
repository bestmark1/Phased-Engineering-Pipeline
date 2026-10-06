---
name: existing-system-pipeline
description: >
  Safely change an existing system you did not build with new-product-pipeline: read-only
  archaeology, an exact test baseline, characterization specs and a parity gate. Use for
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

## Flow — one scenario per run

Paths: `SPECS_DIR`, `STATE_FILE`, `INITIATIVE_DIR` are chosen in step 0 (`references/pipeline-core.md`).
Every role brief ends with the pipeline context block (`references/role-inputs.md`).
Load `references/entry-prompt.md` at the start (steps 0, 2, 3 and OBS decisions) and
`references/parity.md` in every slice that touches the scenario.

| # | Step | Role | May write | Exit gate |
|---|---|---|---|---|
| 0 | Entry: permissions, process map, choose **one** scenario | Coordinator + owner | `STATE_FILE` (PROGRESS.md/HANDOFF.md or an initiative file) | owner approval of scenario and permissions |
| 1 | Archaeology of the scenario's risk zones | Archaeology (`references/archaeology-prompt.md`), source read-only | `<INITIATIVE_DIR>/archaeology-report.md` (+ optional HTML map) | READ-ONLY COMPLETE |
| 2 | Apply AGENTS.md answers and `docs/surprises.md` from the report | Coordinator | AGENTS.md (preserving it), `docs/surprises.md` | step-0 write permission |
| 3 | Read-only access procedures (database, logs, CI) | Coordinator; owner creates credentials | `docs/access/*`, `scripts/access/*` | owner approval of the procedures |
| 4 | Product delta incl. `specs/INDEX.md` → Consistency (`product`) → Architect → Tech Lead → Consistency (`full`) | Product, Consistency, Architect, Tech Lead | `<INITIATIVE_DIR>` artifacts, `<SPECS_DIR>/INDEX.md` (new criteria `planned`) | owner approvals + both Consistency gates |
| 5 | Slice 1 = characterization: smoke + GWT specs of current behavior as `OBS-n`; golden set/eval if an algorithm/LLM; parity baseline | Developer → reviewers → phase QA | `<SPECS_DIR>/`, its `support/`, eval files, `<INITIATIVE_DIR>/parity/` | slice gates + owner's batch OBS decision |
| 6 | Changing slices | Developer → reviewers → phase QA | per plan | core gates + `parity` |
| 7 | Final QA, two passes | QA (`references/qa-prompt.md`) | reports | initiative receipt accepted |
| 8 | Retro, incl. what past agent sessions stumbled on (if transcripts exist) | Retro | docs/pointers | advisory |

Every slice: Developer → self-check → deterministic checks → subtraction pass at Medium/High
→ independent review and phase QA by depth → targeted repair → coordinator validates the
receipt → Done. Local handoff is a valid endpoint; push/PR/deploy follow
`references/gate-policy.md`. A dirty working tree is not permission to stash or overwrite other
work; do not create the same branch twice. Environment: Docker Compose or devcontainer; Nix only
if the project already uses it.

| Phase | Role | Prompt file | When |
|---|------|-------------|------|
| 1 | Archaeology | `references/archaeology-prompt.md` | read-only, once per run |

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
