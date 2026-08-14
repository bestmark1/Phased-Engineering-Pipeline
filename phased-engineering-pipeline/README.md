# phased-engineering-pipeline

> Claude Code skill that orchestrates eleven specialized agents through a full BMAD engineering pipeline: **Narrative → (MRD) → PRD → Clarifier → Architect → Tech Lead → Analyzer → Developer** with SOLID and SRE code reviewers, then **QA validation** and a **session-archaeology retro**. Includes auto git commits, feature branch workflow, CI/CD awareness, `SPEC_PLAN/` artifact hub, knowledge base (`docs/`) with a surprises log, AGENTS.md project map, decision logs, and tech debt tracking.

---

## What it does

Instead of asking Claude to "build a system" and hoping for the best, this skill enforces a professional BMAD engineering workflow with explicit approval gates:

```
[Narrative Lead] → [Market PM: Full mode] → [Product PM] → PRD.md → ⛔ USER APPROVAL
  → [Clarifier] → ⛔ CLARIFY PASS
  → git: create feature/{slug} branch, commit product artifacts
  → [Architect] → ARCHITECTURE.md + CONSTITUTION.md + AGENTS.md + docs/ → ⛔ USER APPROVAL
    → [Tech Lead] → IMPLEMENTATION_PLAN.md (with Decision Log) → ⛔ USER APPROVAL
      → [Analyzer] → cross-artifact-analysis.md → ⛔ ANALYZE PASS
      → loop per vertical slice:
          [Developer] → self-review loop → deterministic gate (build/lint/typecheck/test)
          → [Reviewer SOLID] ‖ [Reviewer SRE]  (topology by review depth)
          → critic loop on findings → APPROVE → next slice
      → [QA Agent] → exercises the running product against every criterion
          → QA PASS → [Release Gate] → RELEASE READY → [Retro]
          → ⛔ OWNER PERMISSION → git: push → gh pr create → ⛔ USER REVIEWS DIFF
```

**Phase 0a — Domain Analysis** — A Domain Analyst researches the problem space, stakeholders, competitors, and risks. Asks 5-8 clarifying questions. Saves distilled vendor docs to `docs/references/{tool}-llms.txt` for reuse.

**Phase 0b — Product Requirements** — A Product Manager converts research into `PRD.md` with user stories (As a / I want / So that), acceptance criteria (Given / When / Then), and success metrics. Every criterion is black-box and names how it will be verified; a **Quality Requirements** table covers security, privacy, performance, accessibility, and data recovery.

**Phase 1 — Architecture** — A Senior Architect reads the official docs, asks 3-5 clarifying questions, then produces:
- `ARCHITECTURE.md` with C4 diagrams (Mermaid), contracts/interfaces, dependency layer order, error handling strategy
- `AGENTS.md` — project map capped at 60 lines, answering five questions: what the project is, where the docs are, how to run the environment, related repos, what is forbidden without permission
- `docs/` knowledge base scaffold per project principles

**Phase 2 — Implementation Plan** — A Tech Lead converts the approved architecture into `IMPLEMENTATION_PLAN.md`. Phases are **vertical slices**, not layers: a walking skeleton first, then one user scenario per phase, hardening last. Each phase states what a user can do that they could not before, carries a runnable Definition of Done including a check against the running product, a review depth, and a **Decision Log** (chose X over Y because…).

**Phase 3 — Coding loop** — For each plan phase: a Senior Developer implements only that phase, performs an explicit **self-review loop** (verify → fix → re-verify), logs deferred items to `docs/tech-debt-tracker.md`, auto-commits, then two reviewers run **in parallel**:
- **Reviewer SOLID** — checks architecture, DI, type safety, naming, layer violations
- **Reviewer SRE** — checks resilience, error boundaries, security, resource leaks

Both must return `APPROVE` before the next phase starts.

**Phase 4 — QA Validation** — A QA Engineer **starts the product** and exercises every acceptance criterion through a real interface — browser, HTTP request, CLI — recording what it observed (`POST /api/session → 201`), not which function it read. Code tracing is for diagnosis only. Also runs build/test/lint, detects scope creep and orphan tests, updates `docs/QUALITY_SCORE.md`. Verdict is `QA PASS`, structured findings, or `QA INCONCLUSIVE`. A criterion that cannot be exercised is `UNKNOWN`, never `PASS`.

**Release Gate** — Before any push or deploy: a clean checkout installs from the lockfile and starts, `.env.example` covers every variable the code reads, migrations run and roll back, a health check answers, and the primary scenario runs end to end. Catches the build that works only in the agent's session. The gate verifies and reports — it never ships.

**Retro** — Session archaeology: where the agent stalled, what context was missing, what got asked twice. Applies minimal fixes to `AGENTS.md` and `docs/` so the next session does not hit the same walls.

**Finish** — With the owner's explicit go-ahead: push feature branch, create PR via `gh pr create`, verify CI checks, owner reviews diff before merge.

---

## New in v2 — Harness Engineering Upgrade

Inspired by OpenAI's [Harness Engineering](https://openai.com/index/harness-engineering/) practices:

| Feature | Description |
|---------|-------------|
| `docs/` knowledge base | Scaffold created by Architect, populated throughout pipeline |
| `AGENTS.md` | Project map (≤60 lines): five questions, pointers instead of prose |
| Decision Log | Each plan phase documents choices made and why |
| Tech Debt Tracker | `docs/tech-debt-tracker.md` — tracked debt is acceptable, hidden is not |
| Self-Review Loop | Developer: verify → self-fix → re-verify before handing off |
| `STRICT_MODE` | `false` = advisory reviews for prototyping, `true` = all gates blocking |
| llms.txt caching | Analyst saves distilled docs once; subsequent agents reuse |
| Quality Score | QA updates `docs/QUALITY_SCORE.md` with coverage grades per layer |
| Layer violations | SOLID reviewer checks dependency flow direction |
| Boring tech principle | Architect avoids "magic" libraries; prefers stable, documented deps |

---

## New in v3 — Gate Discipline

The pipeline's reviewers are themselves LLMs. v3 treats them as such: as fallible judges
that cost money, drift, and share blind spots with the model that wrote the code.

| Feature | Description |
|---------|-------------|
| Evidence hierarchy | Environment checks > tests > contracts > human review > LLM judge. A judge never overrides a stronger source |
| Deterministic-first gates | build / lint / typecheck / test run before any reviewer is invoked — a linter proves for free what an LLM guesses at |
| Review depth by risk | `low` / `medium` / `high` per phase. A config bump does not cost what a payment flow costs |
| Structured verdicts | `criterion` / `status` / `severity` / `evidence` / `fix` / `rubric_version` instead of prose a developer cannot act on |
| `UNKNOWN` verdict | A criterion with no checkable evidence is not a failure. Forcing binary answers manufactures both false approvals and false blocks |
| Critic loop | Fix only the findings, re-review only the failing criteria, escalate after three rounds on one criterion |
| Escalation over repetition | Re-running one reviewer measures judge stability, not code quality. Escalate on uncertainty instead |
| Agent guardrails | Refuse out-of-scope deletion, secret leakage into commits or logs, history rewrites, and unrequested outward-facing actions |
| Run economics | Tokens, duration, cost and review round-trips recorded per phase — report-only until a baseline exists |
| SKILL.md stays lean | Entry point holds the flow, gates and principles; role detail loads from `references/` only when that role runs |
| Eval hooks | Optional `{{EVAL_COMMAND}}` and `SPEC_PLAN/EVAL_PLAN.md` for products containing an LLM. The pipeline calls eval tooling; it does not reimplement metrics or judges |

### Context practices — what the project leaves behind for the next session

| Feature | Description |
|---------|-------------|
| `docs/surprises.md` | Only what an agent cannot derive from general knowledge: workarounds, hidden constraints, dangerous places. Never "what a database is" |
| Short `AGENTS.md` | Capped at 60 lines, five questions, pointers instead of prose. Detail lives in the docs tree |
| Tests are evidence | A test proves a named requirement — an acceptance criterion, an architecture constraint, or a defect that must not return. Traceability, not scarcity: orphan tests are the defect, thorough coverage is not |
| Black-box acceptance criteria | Criteria describe what the user observes, never internals — the implementation stays replaceable |
| Session-archaeology retro | After QA PASS: where the agent stalled, what context was missing, then minimal fixes to `AGENTS.md` and `docs/` |

---

## New in v3.1 — Does it actually work

Documentation and review were the strong parts; proving the product runs was not. v3.1 closes that gap.

| Feature | Description |
|---------|-------------|
| QA exercises the running product | Criteria are verified by starting the product and observing it, not by tracing functions. Evidence is `POST /api/session → 201`, not a file path. No runnable environment means `UNKNOWN`, never `PASS` |
| Release Gate | Clean checkout installs and starts, `.env.example` complete, migrations reversible, health check answers, smoke path runs. Catches the build that works only in the agent's session |
| Vertical slices | Phases are user-visible slices, not layers. A walking skeleton first, one scenario per phase after. Nothing waits until the last phase to work |
| Scope by intent | The plan's file list is an expectation, not a whitelist — lockfiles and generated files need no amendment; an unplanned capability does |
| Artifact change protocol | When implementation proves an approved artifact wrong: update the earliest artifact invalidated, propagate downstream, stop for approval when the change is material |
| Quality requirements | Security, privacy, performance, accessibility and data recovery get stated in the PRD with a verification method — instead of being discovered at release |
| Real exit codes | "Build would pass" is no longer an acceptable result. Commands are run and their exit codes reported, or named as not run with a reason |
| Git hygiene | Clean tree before a phase; stage files by name. `git add .` is how `.env` files and credentials reach commits |

**On repeated runs.** Requiring the same reviewer to pass an artifact k times in a row is
not a reliability gain — repeated calls to one model with one prompt are correlated, and
unanimity rejects correct work at compounding rates (a judge that approves good work 90%
of the time passes it only 73% of the time across three runs). v3 escalates on genuine
uncertainty instead, at roughly 1.1–1.3× cost rather than 3×.

---

## Installation

```bash
# Option A — from .skill file
unzip phased-engineering-pipeline.skill -d ~/.claude/skills/

# Option B — manual
git clone https://github.com/bestmark1/Phased-Engineering-Pipeline.git
cp -r Phased-Engineering-Pipeline/phased-engineering-pipeline ~/.claude/skills/
```

---

## Usage

Claude Code activates this skill automatically when you say things like:

```
Build a Flutter weather tracking app
```
```
Architect and implement a FastAPI analytics service
```
```
Create project: Payment Gateway Proxy in Go
```
```
BMAD pipeline for a new feature
```

---

## Configuration — Stack Profiles

Fill these placeholders before spawning agents. The skill is **tech-stack agnostic**.

| Placeholder | Description | Example (Flutter) |
|---|---|---|
| `{{PROJECT_NAME}}` | Project name | Weather Tracker |
| `{{TECH_STACK}}` | Runtime + language + frameworks | Flutter 3.x, Dart 3.x, Riverpod |
| `{{BUILD_COMMAND}}` | Build verification | `flutter build apk --debug` |
| `{{RUN_COMMAND}}` | Start the product the way a user reaches it | `flutter run -d chrome` |
| `{{TEST_COMMAND}}` | Test runner | `flutter test` |
| `{{LINT_COMMAND}}` | Static analysis | `flutter analyze` |
| `{{QUALITY_RULES}}` | Language-specific quality rules | null safety, no dynamic, const constructors |
| `{{INTERFACE_STYLE}}` | How contracts are defined | abstract class / mixin |
| `{{DOCS_URL}}` | Official docs URL | https://docs.flutter.dev/ |
| `{{STRICT_MODE}}` | Gate enforcement | `true` (default, all gates blocking) |
| `{{PIPELINE_MODE}}` | `lite` or `full` | `lite` |
| `{{TYPECHECK_COMMAND}}` | Type checker if separate | `dart analyze` |
| `{{ROLLBACK_COMMAND}}` | How to undo the last change | `git revert HEAD` |
| `{{DEFAULT_REVIEW_DEPTH}}` | `low` / `medium` / `high` floor | `medium` |
| `{{EVAL_COMMAND}}` | Eval suite; empty when the product has no LLM | `npx promptfoo eval` |

`SKILL.md` holds the full placeholder table.

**Pre-built stack profiles included:** Flutter/Dart, TypeScript/Node.js, Python/FastAPI, Go.

---

## File structure

```
phased-engineering-pipeline/
├── SKILL.md                         # Entry point: flow, gates, principles, role→prompt map
└── references/
    ├── narrative-prompt.md          # Phase 0a: Narrative Lead → Narrative.md
    ├── mrd-prompt.md                # Phase 0a2: Market PM → MRD.md (Full mode only)
    ├── analyst-prompt.md            # Domain Analyst (+ llms.txt caching)
    ├── pm-prompt.md                 # Phase 0b: Product Manager → PRD
    ├── clarify-prompt.md            # Phase 0c: Spec Clarifier
    ├── architect-prompt.md          # Phase 1: Senior System Architect (+ AGENTS.md, docs/)
    ├── tech-lead-prompt.md          # Phase 2: Tech Lead (+ Decision Log, review depth)
    ├── analyze-prompt.md            # Phase 2a: Cross-artifact Analyzer
    ├── developer-prompt.md          # Phase 3: Senior Developer (+ self-review, guardrails)
    ├── reviewer-solid-prompt.md     # Reviewer: Principal Staff Engineer (+ layer violations)
    ├── reviewer-sre-prompt.md       # Reviewer: SRE & Security Auditor
    ├── qa-prompt.md                 # Phase 4: QA Engineer (+ QUALITY_SCORE.md)
    ├── release-prompt.md            # Release Gate: clean checkout, config, rollback, smoke
    ├── retro-prompt.md              # Phase 5: Retro — session archaeology
    ├── progress-template.md         # PROGRESS.md template
    ├── eval-hooks.md                # Eval planning + cold start (only when EVAL_COMMAND is set)
    ├── run-economics.md             # Cost tracking + caching while tuning the pipeline
    └── docs-scaffold.md             # Canonical docs/ tree + restructure policy
```

---

## Knowledge Base (docs/)

Architect creates this structure after Phase 1. Subsequent agents populate it.
The canonical definition lives in `references/docs-scaffold.md`:

```
docs/
├── README.md                 # Index of the knowledge base
├── EXECUTION_RULES.md        # How work is executed in this project
├── surprises.md              # Project-specific surprises only — never general knowledge
├── tech-debt-tracker.md      # Updated by Developer/Reviewers when deferring
├── QUALITY_SCORE.md          # Updated by QA after validation
├── decisions/
│   └── index.md              # Design decisions catalog
├── exec-plans/
│   ├── active/               # Current IMPLEMENTATION_PLAN.md
│   └── completed/            # Archived plans after merge
├── references/
│   └── {tool}-llms.txt       # Distilled vendor docs (from Analyst)
└── archive/                  # Superseded detail moved out during restructures
```

---

## Git & CI/CD Integration

- **Feature branches:** `feature/{slug}` created after PRD approval
- **Auto-commits:** `[phase-N]` format at each gate (PRD, architecture, plan, code, QA)
- **PR creation:** `gh pr create` after QA pass
- **CI awareness:** `gh pr checks` to verify GitHub Actions (lint, test, build)
- **User control:** User reviews diff before merge — agent never merges automatically

---

## Recovery procedures

| Scenario | What happens |
|----------|-------------|
| User rejects PRD | Re-spawn PM with feedback, new approval gate |
| User rejects Architecture | Re-spawn Architect with feedback, new approval gate |
| User rejects Plan | Re-spawn Tech Lead with feedback, new approval gate |
| Developer returns `BLOCKED` | Surface blocker to user, wait for decision |
| Review loop stuck 3+ rounds | Escalate to user: retry / accept / simplify scope |
| QA fails | Developer fixes specific criteria, QA re-validates |
| QA cannot run the product | Report `QA INCONCLUSIVE` with what would make it runnable — never pass on code reading |
| Release Gate blocked | Fix the missing artifact (uncommitted file, absent env var, irreversible migration) and re-run the gate |
| Implementation proves an approved artifact wrong | Update the earliest artifact invalidated, propagate downstream, stop for approval if the change is material |
| CI check fails | Read failure, fix if possible, escalate if infra issue |
| Agent timeout | Re-spawn once, then escalate |

---

## Supported stacks

Works with any stack — all prompts use generic placeholders. Tested profiles:

- **Flutter/Dart** (mobile apps)
- **TypeScript/Node.js** (backend services, Web3)
- **Python/FastAPI** (analytics, ML services)
- **Go/gin** (microservices)

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Claude Code skills support (`~/.claude/skills/`)
- `gh` CLI (for PR creation and CI checks)
- Git (for feature branch workflow)
