---
name: phased-engineering-pipeline
description: |
  Full-system phased engineering with product framing and disciplined execution:
  Narrative, MRD, PRD, clarification, architecture, constitution, phase planning,
  cross-artifact analysis, execution-by-phase, QA validation, and optional Plane MCP sync.
  Includes: SPEC_PLAN/ artifact hub, PROJECT_INDEX.md navigation hub, AGENTS.md project map
  (short five-question formula), CONSTITUTION.md governance, docs/ knowledge base with
  docs/surprises.md, decision logs, tech debt tracking, tests-as-requirements policy,
  black-box acceptance criteria, self-review loop, session-archaeology retro, STRICT_MODE,
  llms.txt reference caching, and execution-state tracking in Plane.
  Gate discipline: deterministic checks before LLM review, review depth by risk,
  structured verdicts with UNKNOWN, critic loop on failure, agent guardrails,
  report-only run economics, and optional eval hooks for LLM-bearing products.
use_when:
  - Building from scratch
  - "Design + plan + code"
  - User says "build", "architect", "implement a full system", "phased pipeline", "BMAD pipeline", "new feature end-to-end"
does_not_handle:
  - Debugging an existing bug with no project framing
  - Single-function edits
  - One-shot fixes with no planning value
---

# Phased Engineering Pipeline v3

Twelve specialized agents. Multiple gates. Feature branches. Phase isolation. Optional Plane MCP sync.

```text
[Narrative Lead] → SPEC_PLAN/Narrative.md
→ [Market PM] → SPEC_PLAN/MRD.md            (Full mode only)
→ [Product PM] → SPEC_PLAN/PRD.md
→ ⛔ USER APPROVAL
→ [Clarifier] → SPEC_PLAN/clarification-report.md
→ ⛔ CLARIFY PASS
→ git: create feature/{slug} branch, mkdir SPEC_PLAN/, commit approved product artifacts
→ [Architect] → SPEC_PLAN/ARCHITECTURE.md + SPEC_PLAN/CONSTITUTION.md + PROJECT_INDEX.md + AGENTS.md + docs/
→ ⛔ USER APPROVAL
→ git: commit architecture artifacts
→ [Tech Lead] → SPEC_PLAN/IMPLEMENTATION_PLAN.md + SPEC_PLAN/phase-registry.md
→ ⛔ USER APPROVAL
→ git: commit execution plan
→ [Analyzer] → SPEC_PLAN/cross-artifact-analysis.md
→ ⛔ ANALYZE PASS
→ [Plane Sync] → optional Plane project/module/cycle/work items + SPEC_PLAN/plane-sync.md
→ loop per implementation phase:
   [Developer: current phase only]
   → self-review loop (verify → fix → re-verify)
   → deterministic gate: build ‖ lint ‖ typecheck ‖ test   ← LLM reviewers not called until green
   → git: commit code
   → [Reviewer SOLID] ‖ [Reviewer SRE]   ← topology set by review depth (Low/Medium/High)
   → findings? critic loop: fix findings only → re-run checks → re-review failing criteria
   → UNKNOWN on a blocking criterion? → escalate to second reviewer, then owner
   → APPROVE → record run cost in PROGRESS.md → update HANDOFF.md / Plane → next phase
→ [QA Agent] → validates PRD acceptance criteria + phase DoD trace
→ issues? → fix → re-validate
→ QA PASS
→ [Release Gate] → clean checkout starts, config complete, rollback works, smoke path
→ ⛔ RELEASE READY
→ [Retro] → session archaeology → minimal improvements to AGENTS.md / docs
→ ⛔ OWNER PERMISSION for any outward-facing action
→ git: push → gh pr create
→ ⛔ USER REVIEWS DIFF
```

## Core principles

1. **Meaning vs execution**
   - Markdown artifacts in repo are the source of truth for meaning:
     strategy, requirements, architecture, rules, decisions, and long-lived context.
   - Plane is the source of truth for execution state:
     open work, active work, blockers, and completion status.

2. **Phase isolation**
   - Developer may execute only the active implementation phase.
   - Future-phase work is deferred unless explicitly allowed by the implementation plan.

3. **Verification over vibes**
   - “Looks good” is not evidence.
   - Every phase must define commands, checks, and observable completion criteria.

4. **Tracked debt is acceptable; hidden debt is not**
   - Deferred work goes to `docs/tech-debt-tracker.md` or the linked Plane item.

5. **Navigation must remain maintainable**
   - Agents may propose restructuring long docs into a parent summary plus child docs.

6. **Tests are evidence of requirements**
   - A test exists to prove that a requirement holds: a PRD acceptance criterion, an
     architecture constraint, or a defect that must not come back.
   - Every test names what it proves. A test that names nothing is an **orphan**: it
     freezes an accidental implementation, and the next session maintains the test
     instead of reconsidering the approach.
   - This is a traceability rule, not a scarcity rule. Internal logic may be covered as
     thoroughly as its requirement demands — a complex algorithm serving one acceptance
     criterion may need many tests, and that is correct.
   - A fixed defect is a valid target: the requirement it proves is "this failure does
     not return."
   - The requirement comes first, the test second. An agent that wants a test for
     something with no requirement has found a missing requirement, not a missing test —
     raise it instead of encoding it.

7. **Document surprises, not general knowledge**
   - `docs/` must capture only what an agent cannot derive from general knowledge:
     strange decisions, workarounds, non-obvious constraints, dangerous places.
   - Never document what a framework or database is.
   - Test for every doc entry: "what breaks the next session if it doesn't know this?"

## Pipeline modes

Choose the lightest mode that preserves quality.

### Lite mode
Use:
- internal tools
- constrained features
- improvements to an existing product
- cases where market framing is already known

Flow:
`Narrative → PRD → Clarifier → Architecture → Plan → Build`

### Full mode
Use:
- net-new products
- unclear ICP / segment / positioning
- roadmap-sensitive initiatives
- strategic work where market framing matters

Flow:
`Narrative → MRD → PRD → Clarifier → Architecture → Plan → Build`

## Configuration

Fill these placeholders before starting. Every `{{PLACEHOLDER}}` in prompts resolves from this table.

| Placeholder | Description | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | Project name | Weather Tracker |
| `{{PIPELINE_MODE}}` | `lite` or `full` | `full` |
| `{{TECH_STACK}}` | Runtime + language + frameworks | Node.js, TypeScript strict, Next.js |
| `{{BUILD_COMMAND}}` | Build verification | `npm run build` |
| `{{RUN_COMMAND}}` | Start the product the way a user reaches it | `npm run dev` |
| `{{TEST_COMMAND}}` | Test runner | `npm test` |
| `{{LINT_COMMAND}}` | Linter / static analysis | `npm run lint` |
| `{{TYPECHECK_COMMAND}}` | Type checker if separate | `tsc --noEmit` |
| `{{QUALITY_RULES}}` | Stack-specific quality rules | strict TS, no `any`, constructor DI |
| `{{INTERFACE_STYLE}}` | Contract style | TypeScript interfaces |
| `{{DOCS_URL}}` | Official docs URL | `https://nextjs.org/docs` |
| `{{ROLLBACK_COMMAND}}` | How to undo last change | `git revert HEAD` |
| `{{STRICT_MODE}}` | `true` blocks gates, `false` advisory | `true` |
| `{{EVAL_COMMAND}}` | Eval suite for LLM behavior; empty when the product has no LLM | `npx promptfoo eval` |
| `{{DEFAULT_REVIEW_DEPTH}}` | `low`, `medium`, or `high` — floor for this project | `medium` |
| `{{PLANE_ENABLED}}` | `true` or `false` | `true` |
| `{{PLANE_PROJECT}}` | Plane project or workspace shorthand | `FIT` |
| `{{PLANE_MODULE}}` | Current stream / epic / module | `Onboarding` |
| `{{PLANE_CYCLE}}` | Current cycle / sprint / milestone | `May-1` |

## Artifact manifest

Required outputs by the end of the pipeline:

- `PROJECT_INDEX.md`
- `AGENTS.md`
- `PROGRESS.md`
- `HANDOFF.md`

Inside `SPEC_PLAN/`:
- `Narrative.md`
- `MRD.md` (Full mode only)
- `PRD.md`
- `clarification-report.md`
- `ARCHITECTURE.md`
- `CONSTITUTION.md`
- `IMPLEMENTATION_PLAN.md`
- `phase-registry.md`
- `cross-artifact-analysis.md`
- `plane-sync.md` (when Plane is enabled)

Inside `docs/` — the tree is defined once, in `references/docs-scaffold.md`:
- `README.md`
- `EXECUTION_RULES.md`
- `surprises.md`
- `tech-debt-tracker.md`
- `QUALITY_SCORE.md`
- subfolders created on first use: `decisions/`, `exec-plans/`, `references/`, `archive/`

## PROGRESS.md template

The Architect creates this file; every later role updates its own row. Status values are
`⬜ Not started`, `🔄 In Progress`, `✅ Done`, `⛔ Blocked`.

```markdown
# Progress — {{PROJECT_NAME}}

Pipeline mode: {{PIPELINE_MODE}} · Strict mode: {{STRICT_MODE}}

| Phase | Role | Artifact | Status | Updated |
|-------|------|----------|--------|---------|
| 0a | Narrative Lead | SPEC_PLAN/Narrative.md | ⬜ | |
| 0a2 | Market PM | SPEC_PLAN/MRD.md | ⬜ | Full mode only |
| 0b | Product PM | SPEC_PLAN/PRD.md | ⬜ | |
| 0c | Clarifier | SPEC_PLAN/clarification-report.md | ⬜ | |
| 1 | Architect | SPEC_PLAN/ARCHITECTURE.md | ⬜ | |
| 2 | Tech Lead | SPEC_PLAN/IMPLEMENTATION_PLAN.md | ⬜ | |
| 2a | Analyzer | SPEC_PLAN/cross-artifact-analysis.md | ⬜ | |
| 3.1 | Developer | <phase 1 scope> | ⬜ | |
| 3.N | Developer | <phase N scope> | ⬜ | |
| 4 | QA | QA report | ⬜ | |
| 4r | Release Gate | Release check report | ⬜ | |
| 5 | Retro | AGENTS.md / docs updates | ⬜ | |

## Run cost per phase

Report-only until a baseline exists — never a gate.

| Phase | Tokens in/out | Duration | Approx. cost | Review round-trips |
|-------|---------------|----------|--------------|--------------------|

## Blockers

| Date | Phase | Blocker | Owner decision needed |
|------|-------|---------|-----------------------|
```

The Architect pre-fills rows `3.1`–`3.N` as placeholders; the Tech Lead replaces them with
the real phases once `IMPLEMENTATION_PLAN.md` exists.

## Required repository structure

```text
PROJECT_INDEX.md
AGENTS.md
PROGRESS.md
HANDOFF.md

SPEC_PLAN/
  Narrative.md
  MRD.md                      # Full mode only
  PRD.md
  clarification-report.md
  ARCHITECTURE.md
  CONSTITUTION.md
  IMPLEMENTATION_PLAN.md
  phase-registry.md
  cross-artifact-analysis.md
  plane-sync.md               # when Plane enabled

docs/                         # full tree: references/docs-scaffold.md
  README.md
  EXECUTION_RULES.md
  surprises.md
  tech-debt-tracker.md
  QUALITY_SCORE.md
  decisions/
  exec-plans/
  references/
  archive/
```

## Role → prompt file

Every role in the flow has a prompt file. A role with no prompt file is a gap in the
skill, not a role the agent should improvise.

| # | Role | Prompt file | When |
|---|------|-------------|------|
| 0a | Narrative Lead | `references/narrative-prompt.md` | always |
| 0a2 | Market PM | `references/mrd-prompt.md` | Full mode only |
| 0b | Product PM | `references/pm-prompt.md` | always |
| 0c | Clarifier | `references/clarify-prompt.md` | always |
| — | Domain Analyst | `references/analyst-prompt.md` | when domain research is needed |
| 1 | Architect | `references/architect-prompt.md` | always |
| 2 | Tech Lead | `references/tech-lead-prompt.md` | always |
| 2a | Analyzer | `references/analyze-prompt.md` | always |
| — | Plane Sync | `references/plane-sync-prompt.md` | `{{PLANE_ENABLED}}=true` |
| 3 | Developer | `references/developer-prompt.md` | per phase |
| 3r | Reviewer SOLID | `references/reviewer-solid-prompt.md` | per review depth |
| 3r | Reviewer SRE | `references/reviewer-sre-prompt.md` | High depth, or Medium when combined |
| 4 | QA | `references/qa-prompt.md` | always |
| 4r | Release Gate | `references/release-prompt.md` | after QA PASS, before push/deploy |
| 5 | Retro | `references/retro-prompt.md` | after QA PASS, advisory |

`references/docs-scaffold.md` is not a role — it is the canonical `docs/` tree definition.

## Role outputs

### 1) Narrative Lead
Produces `SPEC_PLAN/Narrative.md`:
- product story
- why now
- user world / operating context
- top constraints
- non-goals
- obvious risks and assumptions

### 2) Market PM (Full mode)
Produces `SPEC_PLAN/MRD.md`:
- target user / ICP
- JTBD
- alternatives and competitive context
- positioning hypothesis
- success frame and market constraints

### 3) Product PM
Produces `SPEC_PLAN/PRD.md`:
- user stories
- acceptance criteria
- success metrics
- out-of-scope items

### 4) Clarifier
Produces `SPEC_PLAN/clarification-report.md`:
- unanswered questions
- default assumptions chosen
- risk created by missing answers
- what can still proceed safely

### 5) Architect
Produces:
- `SPEC_PLAN/ARCHITECTURE.md`
- `SPEC_PLAN/CONSTITUTION.md`
- `PROJECT_INDEX.md`
- `AGENTS.md`
- `docs/README.md`
- initial `docs/EXECUTION_RULES.md`

`AGENTS.md` is ≤60 lines and answers exactly five questions:
what the project is; where docs are and how to get an outline;
how to run the environment with one command; related repos;
what is forbidden without permission. Pointers, not prose.

### 6) Tech Lead
Produces:
- `SPEC_PLAN/IMPLEMENTATION_PLAN.md`
- `SPEC_PLAN/phase-registry.md`

Each phase in `IMPLEMENTATION_PLAN.md` must include:
- goal
- scope
- exact files touched
- dependencies
- Definition of Done
- verification commands
- rollback notes
- deferred work format

### 7) Analyzer
Produces `SPEC_PLAN/cross-artifact-analysis.md`:
- contradictions across Narrative/MRD/PRD/Architecture/Plan
- missing dependencies
- phase ordering risks
- acceptance criteria with no implementation path
- architecture decisions with no validation path

### 8) Plane Sync (optional but mandatory when Plane is enabled)
Produces/updates:
- Plane work items
- `SPEC_PLAN/plane-sync.md`

### 9) Developer
Implements **only** the current phase.

Before writing code:
- read current phase in `IMPLEMENTATION_PLAN.md`
- confirm scope in `phase-registry.md`
- check or create Plane item if enabled
- move Plane item to `In Progress` if starting execution

During work:
- stay inside phase scope
- log blockers
- record deferred work
- record surprises in `docs/surprises.md` (non-obvious behavior, workarounds, hidden constraints)
- run verification commands

After work:
- update `PROGRESS.md`
- update `HANDOFF.md`
- move Plane item to `Done` only after required validation is complete

### 10) Reviewer SOLID
Checks:
- layering
- dependency direction
- naming and API clarity
- type safety
- contract fidelity
- interface segregation / DI discipline

### 11) Reviewer SRE
Checks:
- resilience
- rollback safety
- error boundaries
- resource handling
- observability hooks
- security and failure mode coverage
- guardrail violations (see Agent guardrails)

### 12) QA Agent
Checks:
- PRD acceptance criteria traceability
- test / build / lint / typecheck exit codes
- scope creep
- quality score updates
- remaining phase gaps

### Verdict format — all reviewers and QA

Free-text verdicts cannot be acted on mechanically and produce fix loops that never
converge. Every reviewing role emits one structured finding per issue:

```json
{
  "criterion": "dependency-direction",
  "status": "FAIL",
  "severity": "blocking",
  "evidence": "src/services/user.ts:42 — UserRepository imports UserService",
  "fix": "Invert the dependency: pass the repository into the service constructor.",
  "rubric_version": "solid-v1"
}
```

- `status` is `PASS`, `FAIL`, or `UNKNOWN`.
- `severity` is `blocking`, `major`, or `minor`.
- `evidence` must name a file and line, a command and its output, or an artifact
  section. A finding with no checkable evidence is not `FAIL` — it is `UNKNOWN`.
- `fix` is one or two sentences. Reviewers never write replacement code.

**`UNKNOWN` is a first-class verdict.** A reviewer that cannot verify a criterion —
missing context, untestable behavior, evidence outside the diff — must say so rather
than guess in either direction. Forcing a binary answer manufactures both false
approvals and false blocks. `UNKNOWN` on a blocking criterion triggers escalation,
not a gate failure.

### Critic loop — how a failed gate converges

A failed gate does not mean re-running the phase. It means one targeted repair:

1. Reviewer returns structured findings.
2. Developer fixes **only the findings**, touching nothing else.
3. Deterministic checks re-run.
4. Reviewer re-examines **only the previously failing criteria**, not the whole diff.

Re-reviewing an entire phase after a two-line fix costs full price for no new
information. If the same criterion fails three rounds in a row, stop and escalate to
the owner — the finding, the fix, or the requirement itself is wrong.

## Plane execution rule

If Plane MCP is available and `{{PLANE_ENABLED}}=true`, Plane is mandatory for execution tracking.

### Responsibility split
- Local markdown artifacts are the source of truth for:
  - strategy
  - product framing
  - requirements
  - architecture
  - implementation planning
  - project rules and context
- Plane is the source of truth for:
  - execution state
  - open work
  - in-progress work
  - completion status
  - blockers
  - operational priority

### Mandatory execution behavior
Before starting implementation work, the agent must:
1. Check the relevant open items in Plane.
2. Identify the item for the current implementation phase.
3. If the work is not yet represented in Plane, create the item first.
4. Move the item to `In Progress` when execution begins.
5. Move the item to `Done` only after implementation and required validation/review are complete.
6. Then select the next highest-priority item from the current module, milestone, or active phase grouping.

### Restrictions
- Do not execute untracked implementation work when Plane is enabled.
- Do not treat markdown files as the live execution board.
- Do not infer completion from code changes alone; update Plane explicitly.
- Do not pull work from future phases unless the implementation plan explicitly allows it.

### Conflict rule
If Plane status and local markdown meaning diverge:
- local markdown artifacts win for scope, meaning, and intent
- Plane wins for current execution status

## Phase isolation rule

Developer may execute only the active implementation phase.

Phases are **vertical slices**: each one ends with something a user can do, cutting
through whatever layers it needs. A phase whose outcome is only "the layer exists" is a
planning defect — see `references/tech-lead-prompt.md`.

Rules:
- Never pull tasks from future phases.
- Scope is about **intent, not a file whitelist**. Touching a file the plan did not list
  is fine when it serves this slice — lockfiles, generated code, a helper discovered
  mid-implementation. Building a capability the plan did not name is not.
- Do not change files outside the current slice's purpose unless:
  1. required for a blocking bug fix inside the current phase, and
  2. recorded in `HANDOFF.md` and `PROGRESS.md`.
- If a needed change belongs to a future phase, log:
  `Deferred to Phase N: <reason>`
- Reviewers review only the current phase diff against:
  - current phase Definition of Done
  - PRD acceptance criteria touched by that phase
  - architecture constraints relevant to that phase

## Documentation restructure policy

Agents must preserve navigability.

Trigger a restructure proposal when:
- a file becomes too long to scan comfortably,
- a file mixes product + architecture + delivery concerns,
- the root index no longer reflects the actual docs tree,
- multiple documents duplicate the same source of truth.

Preferred actions:
1. Split by concern.
2. Keep the parent file as summary + links.
3. Move old detail into `docs/archive/`.
4. Update `PROJECT_INDEX.md`.
5. Record the restructure in `HANDOFF.md` and `PROGRESS.md`.

Agents may propose restructure proactively.
Agents must not silently change canonical meaning during restructure.

## Verification protocol

Claude saying “done” has no engineering value.

Every stage must define how success is observed.

### Verification levels

| Level | Tools | Applies to |
|---|---|---|
| Basic | exit codes, lint, typecheck, unit tests for the phase's own requirements | every coding phase |
| Medium | integration tests, contract tests, smoke tests | QA |
| High | production logs, metrics, manual checklists | post-deploy, outside this skill |

### Exit-code rules
Any required verification command must return exit code 0.
Non-zero exit code = FAIL.
Agent must not continue through a blocking gate.

### Evidence hierarchy

Not all verdicts carry equal weight. Trust evidence in this order, and never let a
weaker source override a stronger one:

1. **Environment / end-state checks** — does the thing actually work when run.
2. **Executable tests and static analysis** — build, test, lint, typecheck exit codes.
3. **Contract checks** — types, interfaces, schemas, API shapes.
4. **Human verdict** — the owner's review of the diff.
5. **LLM judge** — Reviewer and QA verdicts, for what remains subjective.

The model that writes the code and the model that reviews it share blind spots.
An LLM reviewer is the weakest oracle in this list, not the strongest — it is there
to catch what levels 1–4 structurally cannot express, such as architectural intent
or naming clarity.

### Gate order — deterministic checks run first

Within any gate, run cheap deterministic checks **before** invoking an LLM reviewer:

```text
{{BUILD_COMMAND}} → {{LINT_COMMAND}} → {{TYPECHECK_COMMAND}} → {{TEST_COMMAND}}
   → any check FAILED? → return to Developer with the raw output. Do not call a reviewer.
   → all PASSED? → invoke the LLM reviewer(s) for this gate's review depth
```

Rationale: a linter finds a syntax problem for free and with certainty. Paying an LLM
to find the same problem less reliably is waste. LLM reviewers judge logic, architecture
and failure modes — never syntax, formatting, or anything a tool already proves.

### When the product itself contains an LLM

If the product's behavior depends on a model — prompts, agents, RAG, classification,
generation — build/test/lint cannot express whether it works. Tests prove the code runs;
they say nothing about whether the output is any good.

For such projects:

- The Tech Lead defines `{{EVAL_COMMAND}}` and the phase that introduces it.
- Eval criteria are written **before** the implementation phase that needs them, and
  live in `SPEC_PLAN/EVAL_PLAN.md` alongside the acceptance criteria they extend.
- QA runs `{{EVAL_COMMAND}}` as part of Step 3 verification.

This pipeline does **not** implement eval metrics, judges, or datasets itself. Delegate
to dedicated eval skills (rubric design, judge/human alignment, golden datasets,
regression runs) and to established runners — promptfoo for CI-style assertions, Ragas
for retrieval metrics, Inspect AI for agent trajectories. PEP calls them; it does not
reimplement them.

When `{{EVAL_COMMAND}}` is empty, skip this entirely — most projects have no LLM in
the product and need nothing here.

#### Cold start: a new project has no outputs to evaluate

Most eval tooling assumes production traces already exist. A project being built from
scratch has none — there is no code yet, so there is nothing to log. Do not let this
become a reason to defer evaluation until "later", which in practice means never.

Bootstrap in three steps, matched to what actually exists at each point:

**1. Spec-derived cases — available immediately, before any code.**
Every acceptance criterion about model behavior in the PRD is already an eval case.
"Given a Thai greeting, the translation preserves the politeness register" is a test
waiting for an input and an expected property. Write 10–20 such cases into
`SPEC_PLAN/EVAL_PLAN.md` during planning, each with a concrete input and what must be
true of the output. These are hand-written by the owner, not generated — a model
inventing its own success criteria grades its own homework.

**2. First real outputs — after the phase that produces them.**
The moment the LLM path runs end to end, capture its outputs. A few dozen real
responses are enough to see failure patterns the spec never anticipated. This is where
issue-discovery and judge-creation tooling becomes applicable; before this point it has
no input.

**3. Golden dataset and regression — once patterns are known.**
Promote reviewed cases into a golden set and wire `{{EVAL_COMMAND}}` into QA. From here
the normal loop applies: every escaped defect becomes a new case.

Until step 2, `{{EVAL_COMMAND}}` may legitimately run only the spec-derived cases, and
that is enough. An eval suite that covers ten hand-written cases well beats a perfect
methodology that starts after launch.

### Review depth by risk

Not every change deserves the full review topology. Pick depth from the change, not habit.

| Depth | Trigger | Gate |
|---|---|---|
| **Low** | docs, comments, copy, config values, dependency bumps | deterministic checks + one combined review |
| **Medium** | ordinary feature or bugfix inside one phase scope | deterministic checks + one Reviewer + QA against acceptance criteria |
| **High** | auth, payments, data migrations, deletion paths, external API contracts, secrets handling, anything in `SPEC_PLAN/CONSTITUTION.md` marked critical | Reviewer SOLID and Reviewer SRE independently + QA + human diff approval |

When `{{STRICT_MODE}}=true`, High depth cannot be downgraded.
The Tech Lead assigns a depth to each phase in `IMPLEMENTATION_PLAN.md`; the Developer
may raise it, never lower it.

### Escalation instead of repeated runs

Do **not** run the same reviewer multiple times on the same artifact hoping for
agreement. Repeated calls to one model with one prompt produce correlated results:
they measure the judge's stability, not the code's quality, and unanimity requirements
reject correct work at compounding rates.

Escalate only on genuine uncertainty:

1. One reviewer produces a structured verdict.
2. Escalate to a **second, differently-prompted** reviewer only when the verdict is
   `UNKNOWN`, or carries a blocking finding whose evidence field is weak or absent.
3. The two disagree → the owner decides.
4. Periodically (roughly every tenth verdict) re-run one gate blind and compare, to
   keep a feel for how consistent the reviewers actually are.

### Run economics — measure, do not block

Every gate and phase costs real money and time. Record it; do not gate on it yet.

Track per phase in `PROGRESS.md`: tokens in/out, wall-clock duration, approximate cost,
and how many review round-trips the phase needed.

Thresholds stay **report-only** until enough comparable runs exist to know the normal
spread. A cost or latency budget invented before that data is either meaningless or a
source of false failures. Revisit once a baseline exists.

### Cached model calls when iterating on the pipeline itself

When debugging or tuning the pipeline (editing role prompts, reordering gates, changing
models), enable response caching for model calls so repeated runs over unchanged inputs
are free. Paying full price to re-observe an unchanged step is the largest avoidable
cost in pipeline development.

Caching applies to **pipeline development only**. Real project runs must execute
uncached — a cached verdict on changed code is not a verdict.

### Release gate — does it work outside this session

`QA PASS` proves the product satisfies its criteria **here**. It does not prove the
product exists anywhere else. The classic failure is a build that works only in the
agent's session: an uncommitted file, a variable set by hand in one shell, a service
started manually, a migration applied straight to a database.

Before pushing or deploying anything, run `references/release-prompt.md`:

1. **Clean checkout starts** — fresh directory, install from the lockfile, `{{RUN_COMMAND}}`.
2. **Configuration complete** — `.env.example` covers every variable the code reads; no
   real secret anywhere in the repo.
3. **Data changes reversible** — migration runs on empty and on realistic data, and the
   documented rollback restores the previous state.
4. **Health and logging** — the product answers a health check and errors survive in a log.
5. **Smoke path** — the most valuable PRD scenario, end to end, on the clean checkout.

Anything that had to be done by hand is a missing artifact: commit it or record it in
`docs/surprises.md`. Verdict is `RELEASE READY`, `RELEASE BLOCKED`, or `RELEASE UNKNOWN`.

The gate verifies and reports; it never ships. Push, PR, and deploy stay with the owner.

### Agent guardrails

Before executing any command, the Developer must refuse and escalate to the owner when
the action would:

- delete or overwrite outside the current phase's declared file scope,
- run a destructive command against anything but a disposable local target,
- write credentials, tokens, or `.env` contents into a tracked file, a log, or a commit,
- force-push, rewrite published history, or push directly to the default branch,
- perform an outward-facing action (deploy, publish, send, purchase) not named in the
  current phase's Definition of Done.

These are refusals, not warnings. Record each escalation in `HANDOFF.md`.

**Pushing and opening a PR are outward-facing actions.** The flow ends with
`git push → gh pr create`, and that step needs the owner's explicit go-ahead in the
session where it happens — being drawn in the diagram is not standing permission.
Permission covers that one action, not the rest of the session, and never extends to
merging or deploying.

## Pre-execution checklist

Before any code changes:
- [ ] `git status` is clean — leftovers from an earlier session get reviewed or stashed
      first, never swept into this phase's commit
- [ ] Read current phase in `IMPLEMENTATION_PLAN.md`
- [ ] Confirm current phase scope in `phase-registry.md`
- [ ] Check open Plane items if Plane is enabled
- [ ] Confirm the work item exists in Plane
- [ ] Move item to `In Progress` if starting execution
- [ ] Confirm work is inside active phase scope

## Post-execution checklist

Before ending the session or claiming completion:
- [ ] Validate against phase Definition of Done
- [ ] Update `PROGRESS.md`
- [ ] Update `HANDOFF.md`
- [ ] Update `docs/tech-debt-tracker.md` if anything is deferred
- [ ] Update `docs/surprises.md` if anything non-obvious was discovered
- [ ] Move the Plane item to `Done` if complete
- [ ] Note the next highest-priority open item

## Retro: session archaeology

After QA PASS and before opening the PR, run a short retro over the pipeline session itself.
The pipeline must improve the project's working environment for the *next* session.

Answer three questions by walking back through this session's history:
1. **Where did the agent stall?** — repeated attempts, wrong assumptions, dead ends.
2. **What context was missing?** — a doc, a script, a command, an AGENTS.md pointer
   that would have prevented the stall.
3. **What questions came up more than once?** — recurring questions signal a missing doc.

Then apply the smallest possible fixes:
- add a pointer or command to `AGENTS.md` (respect the 60-line cap),
- add an entry to `docs/surprises.md`,
- add or fix a doc in `docs/`,
- record anything larger in `docs/tech-debt-tracker.md`.

Rules:
- This step is advisory, not a blocking gate: no findings → say so in one line and move on.
- Fixes must be minimal and structural (pointers, docs, scripts) — never new process for its own sake.
- Record what was changed in `HANDOFF.md`.

## Recommended git discipline

- Create `feature/{slug}` branch after product approval.
- Commit after each major artifact gate:
  - product artifacts
  - architecture artifacts
  - implementation plan
  - each code phase
  - QA fixes
- Use small, phase-aligned commits.
- Do not combine multiple implementation phases in one commit.
- Stage files by name. `git add .` and `git add -A` are how `.env` files, credentials,
  scratch scripts and build output reach a commit — review the staged diff first.
- Start a phase from a clean working tree.

## Notes for Plane MCP

Plane MCP Server supports multiple transport methods, including HTTP with OAuth, HTTP with PAT token, and Local Stdio for self-hosted instances. Plane documents setup paths for Claude.ai, Claude Desktop, Cursor, VS Code, and other editors, and states that the MCP server enables agents to interact with Plane project-management capabilities.
