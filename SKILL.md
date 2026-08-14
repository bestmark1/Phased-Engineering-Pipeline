---
name: phased-engineering-pipeline
description: |
  Full-system phased engineering with product framing and disciplined execution:
  Narrative, MRD, PRD, clarification, architecture, constitution, phase planning,
  cross-artifact analysis, execution-by-phase, QA validation, release gate, and retro.
  Includes: SPEC_PLAN/ artifact hub, PROJECT_INDEX.md navigation hub, AGENTS.md project map
  (short five-question formula), CONSTITUTION.md governance, docs/ knowledge base with
  docs/surprises.md, decision logs, tech debt tracking, tests-as-evidence policy,
  black-box acceptance criteria, self-review loop, session-archaeology retro, STRICT_MODE,
  and llms.txt reference caching.
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

Eleven specialized agents. Multiple gates. Feature branches. Phase isolation.

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
→ loop per implementation phase:
   [Developer: current phase only]
   → self-review loop (verify → fix → re-verify)
   → deterministic gate: build ‖ lint ‖ typecheck ‖ test   ← LLM reviewers not called until green
   → git: commit code
   → [Reviewer SOLID] ‖ [Reviewer SRE]   ← topology set by review depth (Low/Medium/High)
   → findings? critic loop: fix findings only → re-run checks → re-review failing criteria
   → UNKNOWN on a blocking criterion? → escalate to second reviewer, then owner
   → APPROVE → record run cost in PROGRESS.md → update HANDOFF.md → next phase
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

1. **The repository is the source of truth**
   - Markdown artifacts in repo carry meaning: strategy, requirements, architecture,
     rules, decisions, and long-lived context.
   - `PROGRESS.md` carries execution state: what is open, active, blocked, done.
   - Knowledge that lives only in a chat session does not survive it.

2. **Phase isolation**
   - Developer may execute only the active implementation phase.
   - Future-phase work is deferred unless explicitly allowed by the implementation plan.

3. **Verification over vibes**
   - “Looks good” is not evidence.
   - Every phase must define commands, checks, and observable completion criteria.

4. **Tracked debt is acceptable; hidden debt is not**
   - Deferred work goes to `docs/tech-debt-tracker.md`.

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

Inside `docs/` — the tree is defined once, in `references/docs-scaffold.md`:
- `README.md`
- `EXECUTION_RULES.md`
- `surprises.md`
- `tech-debt-tracker.md`
- `QUALITY_SCORE.md`
- subfolders created on first use: `decisions/`, `exec-plans/`, `references/`, `archive/`

## PROGRESS.md

Execution state for the whole run: one row per phase, plus run cost and blockers.
The Architect creates it from `references/progress-template.md`; every later role
updates its own row. Status values: `⬜ Not started`, `🔄 In Progress`, `✅ Done`, `⛔ Blocked`.

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
| 3 | Developer | `references/developer-prompt.md` | per phase |
| 3r | Reviewer SOLID | `references/reviewer-solid-prompt.md` | per review depth |
| 3r | Reviewer SRE | `references/reviewer-sre-prompt.md` | High depth, or Medium when combined |
| 4 | QA | `references/qa-prompt.md` | always |
| 4r | Release Gate | `references/release-prompt.md` | after QA PASS, before push/deploy |
| 5 | Retro | `references/retro-prompt.md` | after QA PASS, advisory |

`references/docs-scaffold.md` is not a role — it is the canonical `docs/` tree definition.

## Role outputs

Each role's full instructions live in its prompt file (see the table above). This is the
artifact summary — what must exist when the role is done.

| # | Role | Produces |
|---|------|----------|
| 1 | Narrative Lead | `SPEC_PLAN/Narrative.md` — story, why now, user world, constraints, non-goals, risks |
| 2 | Market PM | `SPEC_PLAN/MRD.md` — ICP, JTBD, alternatives, positioning, market constraints (Full mode) |
| 3 | Product PM | `SPEC_PLAN/PRD.md` — user stories, black-box acceptance criteria with verification method, quality requirements, success metrics, non-goals |
| 4 | Clarifier | `SPEC_PLAN/clarification-report.md` — open questions, assumptions taken, risk from missing answers |
| 5 | Architect | `SPEC_PLAN/ARCHITECTURE.md`, `SPEC_PLAN/CONSTITUTION.md`, `PROJECT_INDEX.md`, `AGENTS.md`, `docs/` scaffold |
| 6 | Tech Lead | `SPEC_PLAN/IMPLEMENTATION_PLAN.md`, `SPEC_PLAN/phase-registry.md` |
| 7 | Analyzer | `SPEC_PLAN/cross-artifact-analysis.md` — contradictions, missing dependencies, ordering risks, criteria with no implementation path |
| 8 | Developer | Code for the current slice only, plus updates to `PROGRESS.md`, `HANDOFF.md`, `docs/tech-debt-tracker.md`, `docs/surprises.md` |
| 9 | Reviewer SOLID | Structured findings on layering, dependency direction, naming, type safety, contract fidelity, DI discipline |
| 10 | Reviewer SRE | Structured findings on resilience, rollback safety, error boundaries, resource handling, observability, security, guardrail violations |
| 11 | QA | Validation report: criteria exercised against the running product, exit codes, scope creep, orphan tests, `docs/QUALITY_SCORE.md` |
| — | Release Gate | Release check report: clean checkout, configuration, rollback, health, smoke path |
| — | Retro | Minimal fixes to `AGENTS.md` and `docs/`, recorded in `HANDOFF.md` |

**Every phase in `IMPLEMENTATION_PLAN.md`** must carry: goal, scope, user-visible outcome,
expected files, dependencies, Definition of Done (including a check against the running
product), verification commands, review depth, rollback notes, and the deferred-work format.

**`AGENTS.md`** is ≤60 lines and answers exactly five questions: what the project is;
where docs are and how to get an outline; how to run the environment with one command;
related repos; what is forbidden without permission. Pointers, not prose.

### Verdict format — all reviewers and QA

Free-text verdicts cannot be acted on mechanically and produce fix loops that never
converge. Every reviewing role emits one structured finding per issue, with fields
`criterion`, `status`, `severity`, `evidence`, `fix`, `rubric_version`. The full field
spec lives in each reviewer's own prompt.

- `status` is `PASS`, `FAIL`, or `UNKNOWN`.
- `evidence` must name a file and line, a command and its output, or an artifact section.
  A finding with no checkable evidence is not `FAIL` — it is `UNKNOWN`.
- Reviewers never write replacement code.

**`UNKNOWN` is a first-class verdict.** A reviewer that cannot verify a criterion must say
so rather than guess in either direction; forcing a binary answer manufactures both false
approvals and false blocks. `UNKNOWN` on a blocking criterion triggers escalation, not a
gate failure.

### Critic loop — how a failed gate converges

A failed gate means one targeted repair, not a re-run of the phase:

1. Reviewer returns structured findings.
2. Developer fixes **only the findings**, touching nothing else.
3. Deterministic checks re-run.
4. Reviewer re-examines **only the previously failing criteria**.

Re-reviewing a whole phase after a two-line fix costs full price for no new information.
Three failures on one criterion means the finding, the fix, or the requirement is wrong —
stop and escalate to the owner.

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

## Changing an approved artifact

Implementation discovers things planning could not know: an API behaves differently than
documented, a requirement turns out to be impossible as written, two acceptance criteria
contradict each other only once code exists.

Without a route for this, an agent has two bad options — quietly build something other
than what was approved, or bury the discovery in `tech-debt-tracker.md` and implement the
approved-but-wrong thing. Both produce a product that does not match its own spec.

**Update the earliest artifact the discovery invalidates, then everything downstream.**

| What the discovery changes | Earliest artifact to update |
|---|---|
| What the product does for the user | `SPEC_PLAN/PRD.md` |
| A contract, data shape, or dependency direction | `SPEC_PLAN/ARCHITECTURE.md` |
| Only how a phase is built | `SPEC_PLAN/IMPLEMENTATION_PLAN.md` |
| A project rule or convention | `SPEC_PLAN/CONSTITUTION.md` |

Then propagate: a PRD change flows into architecture, plan, and phase Definition of Done.
Leaving the PRD stale while the code moves on is how a spec quietly becomes fiction.

### When re-approval is required

Ask the owner, and stop, when the change is **material**:

- observable behavior a user would notice,
- a contract other code or an external consumer depends on,
- anything touching data retention, deletion, or migration,
- security, authentication, or permissions,
- cost, or a new external dependency,
- scope: work the approved artifacts did not ask for.

Proceed and simply record the update when the change is **immaterial** — naming,
internal structure, a clarification that changes no behavior, a correction that makes the
artifact say what everyone already assumed.

When in doubt, treat it as material. The cost of one question is minutes; the cost of an
unapproved behavior change discovered at release is the phase.

### Record it

Every artifact change during implementation gets a line in `HANDOFF.md`: what was
discovered, which artifact changed, and whether the owner approved it. A silent edit to
an approved document is indistinguishable from scope creep on review.

## Documentation restructure policy

Agents must preserve navigability: split a file that mixes concerns or grows too long to
scan, keep the parent as summary plus links, move old detail to `docs/archive/`, and
update `PROJECT_INDEX.md`. Agents may propose a restructure proactively, and must never
change canonical meaning while moving text. Full policy: `references/docs-scaffold.md`.

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

When `{{EVAL_COMMAND}}` is set, read `references/eval-hooks.md`: it covers eval planning,
the cold-start bootstrap for a project with no traces yet, and which established runners
to delegate to. This pipeline calls eval tooling; it does not reimplement metrics or judges.

When `{{EVAL_COMMAND}}` is empty, skip this entirely.

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

Every gate and phase costs real money and time. Record tokens, duration, approximate cost
and review round-trips per phase in `PROGRESS.md`. Thresholds stay **report-only** until
enough comparable runs exist to know the normal spread — a budget invented before that
data is either meaningless or a source of false failures.

Details, plus response caching while iterating on the pipeline itself:
`references/run-economics.md`.

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
- [ ] Confirm work is inside active phase scope

## Post-execution checklist

Before ending the session or claiming completion:
- [ ] Validate against phase Definition of Done
- [ ] Update `PROGRESS.md`
- [ ] Update `HANDOFF.md`
- [ ] Update `docs/tech-debt-tracker.md` if anything is deferred
- [ ] Update `docs/surprises.md` if anything non-obvious was discovered
- [ ] Note the next highest-priority open item

## Retro: session archaeology

After QA PASS and before opening the PR, audit the session itself: where the agent
stalled, what context was missing, what got asked more than once. Apply the smallest
structural fixes — a pointer in `AGENTS.md`, an entry in `docs/surprises.md`, a corrected
doc — so the next session does not hit the same walls.

Advisory, never a blocking gate: no findings is a legitimate result, stated in one line.
Fixes are pointers and docs, never new process. Full instructions:
`references/retro-prompt.md`.

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


