---
name: phased-engineering-pipeline
description: |
  Full-system BMAD engineering: analyst research, PRD, spec clarification, architecture, constitution,
  planning, cross-artifact analysis, coding, QA validation.
  Includes: SPEC_PLAN/ artifact hub, AGENTS.md project map, CONSTITUTION.md governance, docs/ knowledge base,
  decision logs, tech debt tracking, enhanced self-review loop, STRICT_MODE for prototyping, llms.txt reference caching.
  Use when: building from scratch, "design + plan + code", user says "build", "architect",
  "implement a full system", "phased pipeline", "BMAD pipeline", "create project", "new feature end-to-end".
  Does NOT handle: debugging existing code, single-function tasks, one-shot fixes.
---

# Phased Engineering Pipeline (BMAD)

Ten specialized agents. Eight gates. Feature branches. Auto-commits.

```
[Analyst] → [PM] → SPEC_PLAN/PRD.md → ⛔ USER APPROVAL
  → [Clarifier] → SPEC_PLAN/clarification-report.md → ⛔ CLARIFY PASS
  → git: create feature/{slug} branch, mkdir SPEC_PLAN/, commit PRD
  → [Architect] → SPEC_PLAN/ARCHITECTURE.md + SPEC_PLAN/CONSTITUTION.md → ⛔ USER APPROVAL → git: commit
    → [Tech Lead] → SPEC_PLAN/IMPLEMENTATION_PLAN.md → ⛔ USER APPROVAL → git: commit
      → [Analyzer] → SPEC_PLAN/cross-artifact-analysis.md → ⛔ ANALYZE PASS
      → loop per plan phase:
          [Developer] → git: commit code
          → [Reviewer SOLID] ‖ [Reviewer SRE]
          → issues? → fix → recommit → re-review
          → both APPROVE → next phase
      → [QA Agent] → validates PRD acceptance criteria
          → issues? → fix → re-validate
          → QA PASS → git: push → gh pr create → ⛔ USER REVIEWS DIFF
```

---

## Configuration

Fill these placeholders before starting. Every `{{PLACEHOLDER}}` in reference prompts resolves from this table.

| Placeholder | Description | Example (Flutter) |
|---|---|---|
| `{{PROJECT_NAME}}` | Project name | Weather Tracker |
| `{{TECH_STACK}}` | Runtime + language + frameworks | Flutter 3.x, Dart 3.x, Riverpod, Dio |
| `{{BUILD_COMMAND}}` | Build verification | `flutter build apk --debug` |
| `{{TEST_COMMAND}}` | Test runner | `flutter test` |
| `{{LINT_COMMAND}}` | Linter / static analysis | `flutter analyze` |
| `{{TYPECHECK_COMMAND}}` | Type checker (if separate) | `dart analyze` / `tsc --noEmit` |
| `{{QUALITY_RULES}}` | Language-specific quality rules | null safety, no dynamic, const constructors, DI |
| `{{INTERFACE_STYLE}}` | How contracts are defined | abstract class / mixin |
| `{{DOCS_URL}}` | Official docs for target platform | https://docs.flutter.dev/ |
| `{{ROLLBACK_COMMAND}}` | How to undo last change | `git revert HEAD` / `git reset --hard HEAD~1` |
| `{{STRICT_MODE}}` | Gate enforcement level | `true` (default) |

<details>
<summary>Stack profile examples</summary>

**TypeScript/Node.js:** `TECH_STACK=Node.js, TypeScript strict` / `BUILD=npm run build` / `TEST=npm test` / `LINT=npm run lint` / `QUALITY=strict: true, no any, DI via constructor` / `INTERFACE=TypeScript interface`

**Python/FastAPI:** `TECH_STACK=Python 3.12, FastAPI, SQLAlchemy` / `BUILD=python -m build` / `TEST=pytest` / `LINT=ruff check .` / `QUALITY=type hints, no bare except, pydantic models` / `INTERFACE=ABC / Protocol`

**Go:** `TECH_STACK=Go 1.23, gin, pgx` / `BUILD=go build ./...` / `TEST=go test ./...` / `LINT=golangci-lint run` / `QUALITY=error wrapping, no naked returns, context propagation` / `INTERFACE=Go interface`
</details>

---

## Artifact Manifest

Documents produced during the pipeline:

- [ ] Domain Research Notes (Phase 0a — Analyst)
- [ ] `SPEC_PLAN/PRD.md` (Phase 0b — PM)
- [ ] `SPEC_PLAN/clarification-report.md` (Phase 0c — Clarifier)
- [ ] `SPEC_PLAN/ARCHITECTURE.md` (Phase 1 — Architect)
- [ ] `SPEC_PLAN/CONSTITUTION.md` (Phase 1 — Architect)
- [ ] `SPEC_PLAN/IMPLEMENTATION_PLAN.md` (Phase 2 — Tech Lead)
- [ ] `SPEC_PLAN/cross-artifact-analysis.md` (Phase 2b — Analyzer)
- [ ] Code + self-review reports (Phase 3 — Developer, per plan phase)
- [ ] Review verdicts (Phase 3 — Reviewers, per plan phase)
- [ ] QA Validation Report (Phase 4 — QA)
- [ ] `AGENTS.md` (Phase 1 — Architect)
- [ ] `docs/` knowledge base scaffold (Phase 1 — Architect)
- [ ] `docs/tech-debt-tracker.md` entries (Phase 3 — Developer/Reviewers)
- [ ] `docs/QUALITY_SCORE.md` (Phase 4 — QA)
- [ ] `PROGRESS.md` (all phases — auto-updated by each agent)
- [ ] `HANDOFF.md` (each phase — written by finishing agent, read by next agent)

---

## Verification Protocol

«Claude говорит, что готово» не имеет инженерной ценности. Каждая стадия должна иметь явное определение «как агент узнает, что сделал правильно» — иначе задача не готова для автономного выполнения.

### Уровни верификации

| Уровень | Инструменты | Применяется |
|---|---|---|
| **Базовый** | exit codes, lint, typecheck, unit tests | Каждая coding-фаза (Phase 3) |
| **Средний** | integration tests, contract tests, smoke tests | QA (Phase 4) |
| **Высокий** | production logs, метрики, ручные чеклисты | После деплоя (вне пайплайна) |

### Правила exit codes

Любая команда верификации **обязана** вернуть exit code 0. Ненулевой exit code = FAIL, агент не продолжает.

```
{{LINT_COMMAND}}       # exit 0 required
{{TYPECHECK_COMMAND}}  # exit 0 required
{{TEST_COMMAND}}       # exit 0 required
{{BUILD_COMMAND}}      # exit 0 required
```

Агент должен явно проверять: `echo "Exit: $?"` или аналог, и включать результат в HANDOFF.md → Status.

### Верификация по стадиям

| Стадия | Команды | Verdict формат | Условие FAIL |
|---|---|---|---|
| Phase 0c (Clarifier) | — (документ) | `CLARIFY PASS` / `CLARIFY FAIL: <список>` | Critical issues найдены |
| Phase 2b (Analyzer) | — (документ) | `ANALYZE PASS` / `ANALYZE FAIL: <список>` | Orphaned items или contradictions |
| Phase 3 (Developer) | lint + typecheck + unit tests | `VERIFY PASS` / `VERIFY FAIL: <команда exit N>` | Любой exit code ≠ 0 |
| Phase 3 (Reviewer) | — (код-ревью) | `APPROVE: Architecture is solid.` / `REJECT: <issues>` | Любое замечание Critical/High |
| Phase 4 (QA) | все три команды + AC coverage | `QA PASS` / `QA FAIL: <список критериев>` | Любой тест упал или AC не покрыт |
| CI | `gh pr checks` | `CI PASS` / `CI FAIL: <check name>` | Любой check ≠ success |

### Rollback условия

Откат выполняется командой `{{ROLLBACK_COMMAND}}` при:
- Developer зафиксировал код, но оба ревьюера вернули REJECT на 3-м и более круге
- QA вернул FAIL и Developer не может исправить без изменения архитектуры
- CI упал по причине infra (не lint/test) — откат до последнего зелёного коммита

### CI как гейт (не advisory)

CI **блокирует** переход к мержу. Если CI упал:
- lint/test/typecheck failure → Developer обязан исправить и перепушить
- build failure → поверхность пользователю, не автофикс
- infra failure → `{{ROLLBACK_COMMAND}}`, поверхность пользователю

> Если не можешь чётко сформулировать «как Claude узнает, что сделал правильно» — задача не готова для автономного выполнения.

---

## Handoff Protocol

Каждая стадия пайплайна — **отдельная сессия или субагент**. Состояние между стадиями передаётся через `HANDOFF.md` в корне проекта. Это сохраняет cache hit rate высоким и контекст чистым.

**Правило:** агент, завершающий стадию, **пишет** `HANDOFF.md`. Агент, начинающий следующую стадию, **читает** его первым делом.

### Шаблон `HANDOFF.md`

```markdown
## Context
Краткое описание: что делали и зачем.

## Decisions
Ключевые архитектурные и технические решения, принятые в этой стадии.

## Changes
Файлы созданы/изменены и что именно изменилось в каждом.

## Status
Текущее состояние — что работает, что нет (pass/fail).

## Next Steps
Что нужно сделать на следующей стадии для продолжения.
```

### Кто пишет → кто читает

| Стадия завершена | Пишет HANDOFF.md | Читает следующий |
|---|---|---|
| Phase 0a (Analyst) | Analyst | PM |
| Phase 0b (PM) | PM | Clarifier |
| Phase 0c (Clarifier) | Clarifier | Architect |
| Phase 1 (Architect) | Architect | Tech Lead |
| Phase 2 (Tech Lead) | Tech Lead | Analyzer |
| Phase 2b (Analyzer) | Analyzer | Developer (phase 3.1) |
| Phase 3.N (Developer) | Developer | Reviewer SOLID + SRE |
| Phase 3.N (Review done) | Reviewers | Developer (next phase) или QA |
| Phase 4 (QA) | QA | — (финал) |

### Правила

- `HANDOFF.md` **перезаписывается** при каждой новой стадии (не накапливается)
- Включается в каждый авто-коммит: `git add HANDOFF.md PROGRESS.md <other files>`
- Раздел **Decisions** обязателен — именно он предотвращает повторные вопросы в новой сессии
- Если агент начинает работу без `HANDOFF.md` — должен запросить у пользователя контекст явно

---

## Task Tool Protocol

Every stage transition must be an **explicit tool call** — not text output. This gives a programmatically verifiable signal that a phase started or ended.

**Rules:**
- At pipeline start: `TaskCreate` one task per phase (status: `pending`)
- When phase begins: `TaskUpdate` → `in_progress`
- When phase ends successfully: `TaskUpdate` → `completed`
- When gate blocks (user approval needed): `TaskUpdate` → `blocked`, notes = what's awaited
- When phase fails / needs redo: `TaskUpdate` → `in_progress` again, notes = reason

**Phase → Task mapping:**

| Phase | TaskCreate title | Notes field |
|-------|-----------------|-------------|
| 0a | `Analyst: domain research` | — |
| 0b | `PM: PRD` | — |
| 0c | `Clarifier: spec clarification` | — |
| 1 | `Architect: architecture + constitution` | — |
| 2 | `Tech Lead: implementation plan` | — |
| 2b | `Analyzer: cross-artifact analysis` | — |
| 3.N | `Developer: phase N — {phase name}` | per plan phase |
| 3.N review | `Review: phase N — SOLID + SRE` | per plan phase |
| 4 | `QA: validation` | — |
| Finish | `Finish: PR + CI` | — |

**Example transition sequence:**
```
TaskUpdate(id, status="completed")           # current phase done
TaskUpdate(id_next, status="in_progress")    # next phase starts
```

> `PROGRESS.md` remains the human-readable record. Task tools provide the machine-verifiable signal. Both must stay in sync.

---

## Progress Tracker

Every agent updates `PROGRESS.md` when starting and finishing their phase. This file is the single source of truth for pipeline status.

```markdown
# {{PROJECT_NAME}} — Progress

| Phase | Agent | Status | Started | Finished | Notes |
|-------|-------|--------|---------|----------|-------|
| 0a Analysis | Analyst | ⏳ Pending | — | — | |
| 0b PRD | PM | ⏳ Pending | — | — | |
| 0c Clarify | Clarifier | ⏳ Pending | — | — | |
| 1 Architecture | Architect | ⏳ Pending | — | — | |
| 2 Plan | Tech Lead | ⏳ Pending | — | — | |
| 2b Analyze | Analyzer | ⏳ Pending | — | — | |
| 3.1 {phase} | Developer | ⏳ Pending | — | — | |
| 3.1 Review | SOLID + SRE | ⏳ Pending | — | — | |
| ... | ... | ... | ... | ... | |
| 4 QA | QA | ⏳ Pending | — | — | |
| Finish | — | ⏳ Pending | — | — | |
```

**Status values:** `⏳ Pending` → `🔄 In Progress` → `✅ Done` / `✅ Approved` / `❌ Rejected` / `🔁 Re-doing`

**Rules:**
- Architect creates `PROGRESS.md` during Phase 1 (scaffold), pre-filling rows from `IMPLEMENTATION_PLAN.md` phases
- Each agent updates their row status + timestamp when starting and finishing
- On rejection / re-review, status changes to `🔁 Re-doing`
- `PROGRESS.md` is committed with every auto-commit (add to `git add` list)

---

## Artifact Hub (`SPEC_PLAN/`)

Every agent saves its primary artifact to `SPEC_PLAN/` at project root. This is the **single source of truth** for all specs and plans — always up-to-date, always in one place.

```
SPEC_PLAN/
├── PRD.md                        # Phase 0b — PM
├── clarification-report.md       # Phase 0c — Clarifier
├── ARCHITECTURE.md               # Phase 1 — Architect
├── CONSTITUTION.md               # Phase 1 — Architect
├── IMPLEMENTATION_PLAN.md        # Phase 2 — Tech Lead
├── cross-artifact-analysis.md    # Phase 2b — Analyzer
└── qa-validation-report.md       # Phase 4 — QA
```

**Rules:**
- Architect creates `SPEC_PLAN/` directory during Phase 1 (scaffold)
- Each agent writes directly to `SPEC_PLAN/<artifact>` (not root, then copy)
- On update/revision (e.g., PRD updated after clarification), overwrite in-place
- `SPEC_PLAN/` is included in every auto-commit: `git add SPEC_PLAN/ PROGRESS.md <other files>`
- Root-level `CONSTITUTION.md` is a **symlink** or copy from `SPEC_PLAN/CONSTITUTION.md` for quick access

---

## Project Knowledge Base

After Phase 1, Architect creates this structure (see `references/docs-scaffold.md` for templates):

```
SPEC_PLAN/                         # ← Artifact Hub (all specs & plans)
CONSTITUTION.md                    # Symlink → SPEC_PLAN/CONSTITUTION.md
docs/
├── design-docs/
│   └── index.md              # Catalog of design decisions
├── exec-plans/
│   ├── active/               # Current IMPLEMENTATION_PLAN.md
│   └── completed/            # Archived plans after merge
├── references/
│   └── {tool}-llms.txt       # Distilled vendor docs (from Analyst)
├── QUALITY_SCORE.md           # Updated by QA after validation
└── tech-debt-tracker.md       # Updated by Developer/Reviewers when deferring
```

- **Analyst** saves distilled docs to `docs/references/{tool}-llms.txt`
- **Architect** creates `SPEC_PLAN/` hub + scaffold + `CONSTITUTION.md`
- **Developer** appends to `tech-debt-tracker.md` when deferring
- **Reviewers** append to `tech-debt-tracker.md` when flagging non-critical issues
- **QA** updates `QUALITY_SCORE.md` after validation + saves report to `SPEC_PLAN/qa-validation-report.md`
- **Tech Lead** moves completed plans to `exec-plans/completed/`

---

## Workflow Checklist

Copy this and track progress:

**Pipeline Init**
- [ ] `TaskCreate` one task per phase (see Task Tool Protocol table above), all status `pending`

**Phase 0a — Domain Analysis**
- [ ] `TaskUpdate(phase-0a, in_progress)`
- [ ] Read `references/analyst-prompt.md`
- [ ] Fill `{{PROJECT_NAME}}`, `{{TECH_STACK}}`, `{{DOCS_URL}}`
- [ ] Spawn Analyst agent → asks 5-8 clarifying questions
- [ ] Answer questions → Analyst produces Domain Research Notes
- [ ] Analyst writes `HANDOFF.md` (Context: project idea; Decisions: scope confirmed; Changes: Domain Research Notes; Status: pass; Next Steps: PM creates PRD)
- [ ] `TaskUpdate(phase-0a, completed)`

**Phase 0b — Product Requirements**
- [ ] `TaskUpdate(phase-0b, in_progress)`
- [ ] Read `HANDOFF.md` ← контекст от Analyst
- [ ] Read `references/pm-prompt.md`
- [ ] Paste Domain Research Notes
- [ ] Spawn PM agent → produces `SPEC_PLAN/PRD.md` with user stories + acceptance criteria
- [ ] PM writes `HANDOFF.md` (Context: PRD created; Decisions: scope/non-goals; Changes: SPEC_PLAN/PRD.md; Status: awaiting approval; Next Steps: Clarifier scans PRD)
- [ ] `TaskUpdate(phase-0b, blocked)` notes="awaiting user PRD approval"
- [ ] ⛔ STOP — wait for user to approve PRD
- [ ] `TaskUpdate(phase-0b, completed)`

**Phase 0c — Spec Clarification**
- [ ] `TaskUpdate(phase-0c, in_progress)`
- [ ] Read `HANDOFF.md` ← контекст от PM
- [ ] Read `references/clarify-prompt.md`
- [ ] Paste approved `SPEC_PLAN/PRD.md` content
- [ ] Spawn Clarifier agent → scans for ambiguities, contradictions, gaps → saves `SPEC_PLAN/clarification-report.md`
- [ ] Clarifier writes `HANDOFF.md` (Context: clarification result; Decisions: resolved ambiguities; Changes: clarification-report.md; Status: PASS or issues; Next Steps: Architect)
- [ ] If `CLARIFY PASS` → `TaskUpdate(phase-0c, completed)` → proceed
- [ ] If critical issues found → present to user → resolve → update `SPEC_PLAN/PRD.md` → re-run

**Feature Branch Creation**
- [ ] Derive `{slug}` from PRD title (kebab-case, e.g. `weather-tracker`)
- [ ] `mkdir -p SPEC_PLAN && git checkout -b feature/{slug}`
- [ ] Commit: `git add SPEC_PLAN/PRD.md && git commit -m "[phase-0] PRD: {project}"`

**Phase 1 — Architecture**
- [ ] `TaskUpdate(phase-1, in_progress)`
- [ ] Read `HANDOFF.md` ← контекст от Clarifier
- [ ] Read `references/architect-prompt.md`
- [ ] Provide approved PRD summary as `{{PRD_SUMMARY}}`
- [ ] Spawn Architect agent → asks 3-5 clarifying questions → produces `SPEC_PLAN/ARCHITECTURE.md` + `SPEC_PLAN/CONSTITUTION.md`
- [ ] Architect writes `HANDOFF.md` (Context: architecture designed; Decisions: tech choices, layer structure; Changes: ARCHITECTURE.md, CONSTITUTION.md, AGENTS.md, docs/; Status: awaiting approval; Next Steps: Tech Lead creates plan)
- [ ] `TaskUpdate(phase-1, blocked)` notes="awaiting user architecture approval"
- [ ] ⛔ STOP — wait for user to approve architecture
- [ ] `TaskUpdate(phase-1, completed)`
- [ ] Commit: `git add SPEC_PLAN/ AGENTS.md docs/ HANDOFF.md && git commit -m "[phase-1] architecture: {project}"`

**Phase 2 — Implementation Plan**
- [ ] `TaskUpdate(phase-2, in_progress)`
- [ ] Read `HANDOFF.md` ← контекст от Architect
- [ ] Read `references/tech-lead-prompt.md`
- [ ] Paste approved architecture summary
- [ ] Spawn Tech Lead agent → produces `SPEC_PLAN/IMPLEMENTATION_PLAN.md`
- [ ] Tech Lead writes `HANDOFF.md` (Context: plan created; Decisions: phase split, DoD per phase; Changes: IMPLEMENTATION_PLAN.md; Status: awaiting approval; Next Steps: Analyzer checks consistency)
- [ ] `TaskUpdate(phase-2, blocked)` notes="awaiting user plan approval"
- [ ] ⛔ STOP — wait for user to approve plan
- [ ] `TaskUpdate(phase-2, completed)`
- [ ] Commit: `git add SPEC_PLAN/IMPLEMENTATION_PLAN.md HANDOFF.md && git commit -m "[phase-2] plan: {project}"`

**Phase 2b — Cross-Artifact Analysis**
- [ ] `TaskUpdate(phase-2b, in_progress)`
- [ ] Read `HANDOFF.md` ← контекст от Tech Lead
- [ ] Read `references/analyze-prompt.md`
- [ ] Provide `SPEC_PLAN/PRD.md`, `SPEC_PLAN/ARCHITECTURE.md`, `SPEC_PLAN/IMPLEMENTATION_PLAN.md`
- [ ] Spawn Analyzer agent → checks coverage, consistency, terminology → saves `SPEC_PLAN/cross-artifact-analysis.md`
- [ ] Analyzer writes `HANDOFF.md` (Context: cross-artifact check; Decisions: resolved gaps; Changes: cross-artifact-analysis.md; Status: PASS or issues; Next Steps: Developer starts phase 3.1)
- [ ] If `ANALYZE PASS` → `TaskUpdate(phase-2b, completed)` → proceed to coding
- [ ] If inconsistencies found → resolve → re-run Analyzer

**Phase 3 — Coding (repeat per plan phase)**
- [ ] `TaskUpdate(phase-3.N, in_progress)`
- [ ] Read `HANDOFF.md` ← контекст от предыдущей стадии
- [ ] Read `references/developer-prompt.md`
- [ ] Fill `{{CURRENT_PHASE}}`, `{{PHASE_DESCRIPTION}}`, `{{FILES_TO_CREATE}}`
- [ ] Spawn Developer agent → produces code + self-review report
- [ ] Developer writes `HANDOFF.md` (Context: phase N implemented; Decisions: implementation choices; Changes: list of files; Status: self-review pass; Next Steps: SOLID + SRE review)
- [ ] Commit: `git add <phase files> HANDOFF.md && git commit -m "[phase-3.N] implement: {phase name}"`
- [ ] `TaskUpdate(phase-3.N-review, in_progress)`
- [ ] Spawn Reviewer SOLID (`references/reviewer-solid-prompt.md`) IN PARALLEL with:
- [ ] Spawn Reviewer SRE (`references/reviewer-sre-prompt.md`)
- [ ] Both return `APPROVE` → Reviewers write `HANDOFF.md` (Status: both APPROVE; Next Steps: next phase or QA) → `TaskUpdate(phase-3.N-review, completed)` → `TaskUpdate(phase-3.N, completed)` → next plan phase
- [ ] Any reviewer returns issues → Developer fixes → recommit → re-run BOTH reviewers
- [ ] Repeat review loop until `APPROVE` from both

**Phase 4 — QA Validation**
- [ ] `TaskUpdate(phase-4, in_progress)`
- [ ] Read `HANDOFF.md` ← контекст от последнего Developer/Review
- [ ] Read `references/qa-prompt.md`
- [ ] Provide PRD.md + all project code
- [ ] Spawn QA agent → extracts acceptance criteria → traces code → runs `{{TEST_COMMAND}}` + `{{BUILD_COMMAND}}` + `{{LINT_COMMAND}}`
- [ ] QA writes `HANDOFF.md` (Context: QA validation; Decisions: —; Changes: qa-validation-report.md; Status: QA PASS or failures; Next Steps: push + PR)
- [ ] QA returns `QA PASS` → `TaskUpdate(phase-4, completed)` → proceed to finish
- [ ] QA returns issues → Developer fixes → recommit → QA re-validates

**Finish**
- [ ] `TaskUpdate(finish, in_progress)`
- [ ] `git push -u origin feature/{slug}`
- [ ] `gh pr create --title "feat: {project}" --body "PRD + Architecture + N phases implemented. QA passed."`
- [ ] Verify CI checks: `gh pr checks`
- [ ] `TaskUpdate(finish, blocked)` notes="awaiting user merge decision"
- [ ] ⛔ STOP — user reviews diff, decides merge
- [ ] `TaskUpdate(finish, completed)`
- [ ] Trigger `finishing-a-development-branch` skill

---

## Phase 0a: Analyst Agent

**When to spawn:** At the very start — before any technical decisions.

**Provide to agent:** Project idea (1-2 sentences), `{{TECH_STACK}}`, `{{DOCS_URL}}`

**Expected output:** Domain Research Notes covering: problem space, stakeholders, existing solutions, domain terminology, risks, constraints, open questions. If `{{DOCS_URL}}` provided, also saves distilled reference to `docs/references/{tool}-llms.txt`.

Read full prompt: `references/analyst-prompt.md`

---

## Phase 0b: Product Manager Agent

**When to spawn:** After Analyst completes research.

**Provide to agent:** Domain Research Notes from Analyst.

**Expected output:** `SPEC_PLAN/PRD.md` containing: problem statement, goals/non-goals, user stories (As a / I want / So that), acceptance criteria (Given / When / Then), success metrics. Every user story must have ≥2 acceptance criteria.

Read full prompt: `references/pm-prompt.md`

---

## Phase 0c: Spec Clarifier Agent

**When to spawn:** After user approves `PRD.md`, before Architecture.

**Provide to agent:** Full `SPEC_PLAN/PRD.md` content.

**Expected output:** `SPEC_PLAN/clarification-report.md` with:
- Ambiguity scan (vague language, missing edge cases, undefined terms)
- Contradiction check (conflicting user stories or acceptance criteria)
- Gap analysis (incomplete flows, untestable criteria)
- Dependency check (unconstrained external dependencies, unspecified ordering)
- Binary verdict: `CLARIFY PASS` or detailed report with Critical/Warning issues + Questions for Product Owner

**If critical issues found:** Present to user, resolve, update `SPEC_PLAN/PRD.md` before proceeding.

Read full prompt: `references/clarify-prompt.md`

---

## Phase 1: Architect Agent

**When to spawn:** After user explicitly approves `SPEC_PLAN/PRD.md`.

**Provide to agent:** PRD summary, `{{PROJECT_NAME}}`, `{{TECH_STACK}}`, `{{DOCS_URL}}`

**Expected output:**
- `SPEC_PLAN/ARCHITECTURE.md` with C4 diagrams (Mermaid), contracts/interfaces (`{{INTERFACE_STYLE}}`), dependency layer order, error handling strategy, PRD Traceability Matrix
- `SPEC_PLAN/CONSTITUTION.md` — project governance: principles, quality rules, coding conventions, dependency rules, review standards, scope boundaries
- `AGENTS.md` — project map (~100 lines): pointers to key files, entry points, conventions
- `docs/` scaffold — knowledge base structure per `references/docs-scaffold.md`

**Design principle:** Prefer stable, well-documented dependencies with good training set coverage. Avoid "magic" libraries.

Read full prompt: `references/architect-prompt.md`

---

## Phase 2: Tech Lead Agent

**When to spawn:** After user explicitly approves `SPEC_PLAN/ARCHITECTURE.md`.

**Provide to agent:** Approved architecture summary + PRD acceptance criteria.

**Expected output:** `SPEC_PLAN/IMPLEMENTATION_PLAN.md` with sequential phases, each containing: files to create, contracts to implement, Definition of Done (`{{TEST_COMMAND}}` / `{{BUILD_COMMAND}}`), Decision Log (chose X over Y because...), PRD coverage per phase.

Read full prompt: `references/tech-lead-prompt.md`

---

## Phase 2b: Cross-Artifact Analyzer Agent

**When to spawn:** After user approves `SPEC_PLAN/IMPLEMENTATION_PLAN.md`, before coding starts.

**Provide to agent:** `SPEC_PLAN/PRD.md`, `SPEC_PLAN/ARCHITECTURE.md`, `SPEC_PLAN/IMPLEMENTATION_PLAN.md`.

**Expected output:** `SPEC_PLAN/cross-artifact-analysis.md` with:
- PRD → Architecture coverage (every user story maps to a component)
- Architecture → Plan coverage (every component has implementation phases)
- Plan → PRD AC mapping (every acceptance criterion has a plan phase)
- Terminology consistency check (same terms used across all 3 documents)
- Constraint propagation check (non-functional requirements flow through all artifacts)
- Binary verdict: `ANALYZE PASS` or detailed report with Coverage Matrix, Inconsistencies, Orphaned Items

**If inconsistencies found:** Resolve (update relevant artifact) → re-run Analyzer.

Read full prompt: `references/analyze-prompt.md`

---

## Phase 3: Developer + Review Loop

**When to spawn:** After user explicitly approves `IMPLEMENTATION_PLAN.md`.

**Per plan phase:**
1. Spawn Developer for current phase only (constraint: STOP after this phase)
2. Developer performs self-review loop:
   - Run `{{LINT_COMMAND}}` → must exit 0
   - Run `{{TYPECHECK_COMMAND}}` → must exit 0
   - Run `{{TEST_COMMAND}}` → must exit 0, 0 failures
   - If any fails → fix → re-run that command → repeat until all exit 0
   - Output explicit verdict: `VERIFY PASS` or `VERIFY FAIL: <command> exited <N>`
3. Developer logs any deferred items to `docs/tech-debt-tracker.md`
4. Auto-commit phase code
5. Spawn both reviewers IN PARALLEL with Developer's output
6. Gate: both must return exact strings:
   - `APPROVE: Architecture is solid.`
   - `APPROVE: System is secure and resilient.`
7. If either returns issues: Developer fixes → self-review again → recommit → both reviewers re-run
8. Mark phase complete. Move to next plan phase.

Read full prompts:
- Developer: `references/developer-prompt.md`
- Reviewer SOLID: `references/reviewer-solid-prompt.md`
- Reviewer SRE: `references/reviewer-sre-prompt.md`

---

## Phase 4: QA Agent

**When to spawn:** After ALL coding phases pass both reviewers.

**Provide to agent:** `SPEC_PLAN/PRD.md` (full) + all project source code.

**Expected output:** QA Validation Report with:
- Acceptance criteria coverage table (criterion → code location → status)
- `{{TEST_COMMAND}}`, `{{BUILD_COMMAND}}`, `{{LINT_COMMAND}}` results
- Scope creep detection (code that exists but no PRD criterion covers it)
- Binary verdict: `QA PASS` or failure list

Read full prompt: `references/qa-prompt.md`

---

## Auto-Commit Protocol

Agents commit automatically at each gate. Format: `[phase-N]` prefix.

| Trigger | Commit Message | Files |
|---------|---------------|-------|
| PRD approved | `[phase-0] PRD: {project}` | `SPEC_PLAN/PRD.md`, `HANDOFF.md` |
| Clarification resolved | `[phase-0c] clarify: {project}` | `SPEC_PLAN/clarification-report.md`, `SPEC_PLAN/PRD.md` (if updated), `HANDOFF.md` |
| Architecture approved | `[phase-1] architecture: {project}` | `SPEC_PLAN/ARCHITECTURE.md`, `SPEC_PLAN/CONSTITUTION.md`, `AGENTS.md`, `docs/`, `HANDOFF.md` |
| Plan approved | `[phase-2] plan: {project}` | `SPEC_PLAN/IMPLEMENTATION_PLAN.md`, `HANDOFF.md` |
| Analysis passed | `[phase-2b] analyze: {project}` | `SPEC_PLAN/cross-artifact-analysis.md`, `HANDOFF.md` |
| Coding phase N passes review | `[phase-3.N] implement: {phase name}` | All phase files, `HANDOFF.md` |
| Developer fix after review | `[phase-3.N] fix: {issue summary}` | Changed files, `HANDOFF.md` |
| QA passes | `[phase-4] QA validation passed` | `SPEC_PLAN/qa-validation-report.md`, test files if any, `HANDOFF.md` |

Rules:
- Use `git add <specific files>` — never `git add .` or `git add -A`
- Always include `PROGRESS.md` in every commit: `git add PROGRESS.md <other files>`
- Commit message must be a single line, no body
- Do NOT push until all phases complete (push only at Finish)

---

## Stop Conditions

| Gate | Trigger | Action |
|------|---------|--------|
| After Phase 0b | `PRD.md` produced | Show to user. Wait for approval. |
| After Phase 0c | Clarifier returns non-PASS | Present critical issues → resolve → update PRD. |
| After Phase 1 | `ARCHITECTURE.md` produced | Show to user. Wait for approval. |
| After Phase 2 | `IMPLEMENTATION_PLAN.md` produced | Show to user. Wait for approval. |
| After Phase 2b | Analyzer returns non-PASS | Resolve inconsistencies → re-run Analyzer. |
| Review issue | Either reviewer returns non-APPROVE | Developer fixes → re-run BOTH reviewers. |
| QA issue | QA returns non-PASS | Developer fixes → QA re-validates. |
| PR created | CI results available | Show to user. User decides merge. |

Do not proceed past a ⛔ gate without user writing approval in chat.

**`{{STRICT_MODE}}` = `false` (prototype mode):** PRD/Architecture/Plan gates remain blocking. Review and QA gates become advisory — log issues but don't block progress. Useful for rapid prototyping where speed > correctness.

---

## CI/CD Awareness

After `gh pr create`, check CI status:

```
gh pr checks --watch
```

- **All checks pass** → notify user, ready for merge review
- **Check fails** → read failure log: `gh pr checks --json name,state,description`
  - If lint/analyze failure → Developer fixes → recommit → push
  - If test failure → Developer fixes → recommit → push
  - If build failure → surface to user (may need config change)
- CI is **a hard gate** — do not present PR as ready until all checks pass (lint/test/build failures must be fixed)

Expected CI pipeline (GitHub Actions on push to main):
1. `{{LINT_COMMAND}}`
2. `{{TEST_COMMAND}}`
3. `{{BUILD_COMMAND}}`

---

## Examples

### Example 1 — Flutter Mobile App

```
PROJECT_NAME:    Weather Tracker
TECH_STACK:      Flutter 3.x, Dart 3.x, Riverpod, Dio, Hive
BUILD_COMMAND:   flutter build apk --debug
TEST_COMMAND:    flutter test
LINT_COMMAND:    flutter analyze
QUALITY_RULES:   null safety, no dynamic, const constructors, DI via Riverpod
INTERFACE_STYLE: abstract class / mixin
DOCS_URL:        https://docs.flutter.dev/
```

### Example 2 — Go Microservice

```
PROJECT_NAME:    Payment Gateway Proxy
TECH_STACK:      Go 1.23, gin, pgx, Stripe SDK
BUILD_COMMAND:   go build ./...
TEST_COMMAND:    go test ./...
LINT_COMMAND:    golangci-lint run
QUALITY_RULES:   error wrapping, no naked returns, context propagation
INTERFACE_STYLE: Go interface
DOCS_URL:        https://stripe.com/docs/api
```

---

## Recovery Procedures

### User rejects PRD (Phase 0b)
1. Ask: "What's missing? Scope too wide? Wrong user stories?"
2. Re-spawn PM with original research notes + user feedback
3. Present revised `PRD.md` — ⛔ STOP again for approval

### User rejects Architecture (Phase 1)
1. Ask: "What needs to change — diagrams, interfaces, error strategy?"
2. Re-spawn Architect with original prompt + user feedback
3. Architect may skip clarifying questions if already answered
4. Present revised `ARCHITECTURE.md` — ⛔ STOP again

### User rejects Implementation Plan (Phase 2)
1. Ask: "Too many phases? Wrong file structure? Missing DoD?"
2. Re-spawn Tech Lead with approved `ARCHITECTURE.md` + user feedback
3. Present revised `IMPLEMENTATION_PLAN.md` — ⛔ STOP again

### Developer returns BLOCKED
1. Surface the exact blocker to the user verbatim
2. Ask: "Should I (a) adjust the architecture, (b) skip this file, or (c) proceed with a stub?"
3. Re-spawn Developer with same phase prompt + resolution
4. Do NOT proceed to reviewers until Developer returns non-BLOCKED report

### Review loop stuck (3+ rounds without both APPROVE)
1. Show user the outstanding issues from the last review round
2. Ask: "Should I (a) let Developer try again, (b) accept as-is, or (c) simplify phase scope?"
3. Do NOT auto-continue. User decides.

### QA fails after all coding phases
1. Show QA failure report to user
2. Developer fixes specific failing acceptance criteria
3. Recommit fixes with `[phase-4] fix: {criterion}`
4. Re-run QA agent — only on previously-failing criteria if possible

### CI check fails after PR
1. Read failure details: `gh pr checks --json name,state,description`
2. If fixable (lint/test) → Developer fixes → push → re-check
3. If infra issue → surface to user, do not auto-fix

### Agent produces no output / times out
1. Re-spawn the same agent with identical prompt (transient failure)
2. If second attempt also fails — surface to user with exact agent name and phase

---

## Integration

- **Feature isolation:** Use `using-git-worktrees` skill if user prefers worktree-based isolation instead of branch switching
- **Finish flow:** After QA pass + PR created, trigger `finishing-a-development-branch` skill for merge/cleanup options
- **Parallel agents:** Phase 3 reviewers run in parallel — use `dispatching-parallel-agents` skill
