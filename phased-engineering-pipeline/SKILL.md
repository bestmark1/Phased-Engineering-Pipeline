---
name: phased-engineering-pipeline
description: |
  Full-system BMAD engineering: analyst research, PRD, architecture, planning, coding, QA validation.
  Use when: building from scratch, "design + plan + code", user says "build", "architect",
  "implement a full system", "phased pipeline", "BMAD pipeline", "create project", "new feature end-to-end".
  Does NOT handle: debugging existing code, single-function tasks, one-shot fixes.
---

# Phased Engineering Pipeline (BMAD)

Eight specialized agents. Six gates. Feature branches. Auto-commits.

```
[Analyst] → [PM] → PRD.md → ⛔ USER APPROVAL
  → git: create feature/{slug} branch, commit PRD
  → [Architect] → ARCHITECTURE.md → ⛔ USER APPROVAL → git: commit
    → [Tech Lead] → IMPLEMENTATION_PLAN.md → ⛔ USER APPROVAL → git: commit
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
| `{{QUALITY_RULES}}` | Language-specific quality rules | null safety, no dynamic, const constructors, DI |
| `{{INTERFACE_STYLE}}` | How contracts are defined | abstract class / mixin |
| `{{DOCS_URL}}` | Official docs for target platform | https://docs.flutter.dev/ |
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
- [ ] `PRD.md` (Phase 0b — PM)
- [ ] `ARCHITECTURE.md` (Phase 1 — Architect)
- [ ] `IMPLEMENTATION_PLAN.md` (Phase 2 — Tech Lead)
- [ ] Code + self-review reports (Phase 3 — Developer, per plan phase)
- [ ] Review verdicts (Phase 3 — Reviewers, per plan phase)
- [ ] QA Validation Report (Phase 4 — QA)
- [ ] `AGENTS.md` (Phase 1 — Architect)
- [ ] `docs/` knowledge base scaffold (Phase 1 — Architect)
- [ ] `docs/tech-debt-tracker.md` entries (Phase 3 — Developer/Reviewers)
- [ ] `docs/QUALITY_SCORE.md` (Phase 4 — QA)

---

## Project Knowledge Base

After Phase 1, Architect creates this structure (see `references/docs-scaffold.md` for templates):

```
docs/
├── design-docs/
│   ├── index.md              # Catalog of design decisions
│   └── core-beliefs.md       # Project principles
├── exec-plans/
│   ├── active/               # Current IMPLEMENTATION_PLAN.md
│   └── completed/            # Archived plans after merge
├── references/
│   └── {tool}-llms.txt       # Distilled vendor docs (from Analyst)
├── QUALITY_SCORE.md           # Updated by QA after validation
└── tech-debt-tracker.md       # Updated by Developer/Reviewers when deferring
```

- **Analyst** saves distilled docs to `docs/references/{tool}-llms.txt`
- **Architect** creates scaffold + populates `core-beliefs.md`
- **Developer** appends to `tech-debt-tracker.md` when deferring
- **Reviewers** append to `tech-debt-tracker.md` when flagging non-critical issues
- **QA** updates `QUALITY_SCORE.md` after validation
- **Tech Lead** moves completed plans to `exec-plans/completed/`

---

## Workflow Checklist

Copy this and track progress:

**Phase 0a — Domain Analysis**
- [ ] Read `references/analyst-prompt.md`
- [ ] Fill `{{PROJECT_NAME}}`, `{{TECH_STACK}}`, `{{DOCS_URL}}`
- [ ] Spawn Analyst agent → asks 5-8 clarifying questions
- [ ] Answer questions → Analyst produces Domain Research Notes

**Phase 0b — Product Requirements**
- [ ] Read `references/pm-prompt.md`
- [ ] Paste Domain Research Notes
- [ ] Spawn PM agent → produces `PRD.md` with user stories + acceptance criteria
- [ ] ⛔ STOP — wait for user to approve PRD

**Feature Branch Creation**
- [ ] Derive `{slug}` from PRD title (kebab-case, e.g. `weather-tracker`)
- [ ] `git checkout -b feature/{slug}`
- [ ] Commit: `git add PRD.md && git commit -m "[phase-0] PRD: {project}"`

**Phase 1 — Architecture**
- [ ] Read `references/architect-prompt.md`
- [ ] Provide approved PRD summary as `{{PRD_SUMMARY}}`
- [ ] Spawn Architect agent → asks 3-5 clarifying questions → produces `ARCHITECTURE.md`
- [ ] ⛔ STOP — wait for user to approve architecture
- [ ] Commit: `git add ARCHITECTURE.md AGENTS.md docs/ && git commit -m "[phase-1] architecture: {project}"`

**Phase 2 — Implementation Plan**
- [ ] Read `references/tech-lead-prompt.md`
- [ ] Paste approved architecture summary
- [ ] Spawn Tech Lead agent → produces `IMPLEMENTATION_PLAN.md`
- [ ] ⛔ STOP — wait for user to approve plan
- [ ] Commit: `git add IMPLEMENTATION_PLAN.md && git commit -m "[phase-2] plan: {project}"`

**Phase 3 — Coding (repeat per plan phase)**
- [ ] Read `references/developer-prompt.md`
- [ ] Fill `{{CURRENT_PHASE}}`, `{{PHASE_DESCRIPTION}}`, `{{FILES_TO_CREATE}}`
- [ ] Spawn Developer agent → produces code + self-review report
- [ ] Commit: `git add <phase files> && git commit -m "[phase-3.N] implement: {phase name}"`
- [ ] Spawn Reviewer SOLID (`references/reviewer-solid-prompt.md`) IN PARALLEL with:
- [ ] Spawn Reviewer SRE (`references/reviewer-sre-prompt.md`)
- [ ] Both return `APPROVE` → mark phase done → next plan phase
- [ ] Any reviewer returns issues → Developer fixes → recommit → re-run BOTH reviewers
- [ ] Repeat review loop until `APPROVE` from both

**Phase 4 — QA Validation**
- [ ] Read `references/qa-prompt.md`
- [ ] Provide PRD.md + all project code
- [ ] Spawn QA agent → extracts acceptance criteria → traces code → runs `{{TEST_COMMAND}}` + `{{BUILD_COMMAND}}` + `{{LINT_COMMAND}}`
- [ ] QA returns `QA PASS` → proceed to finish
- [ ] QA returns issues → Developer fixes → recommit → QA re-validates

**Finish**
- [ ] `git push -u origin feature/{slug}`
- [ ] `gh pr create --title "feat: {project}" --body "PRD + Architecture + N phases implemented. QA passed."`
- [ ] Verify CI checks: `gh pr checks`
- [ ] ⛔ STOP — user reviews diff, decides merge
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

**Expected output:** `PRD.md` containing: problem statement, goals/non-goals, user stories (As a / I want / So that), acceptance criteria (Given / When / Then), success metrics. Every user story must have ≥2 acceptance criteria.

Read full prompt: `references/pm-prompt.md`

---

## Phase 1: Architect Agent

**When to spawn:** After user explicitly approves `PRD.md`.

**Provide to agent:** PRD summary, `{{PROJECT_NAME}}`, `{{TECH_STACK}}`, `{{DOCS_URL}}`

**Expected output:**
- `ARCHITECTURE.md` with C4 diagrams (Mermaid), contracts/interfaces (`{{INTERFACE_STYLE}}`), dependency layer order, error handling strategy, PRD Traceability Matrix
- `AGENTS.md` — project map (~100 lines): pointers to key files, entry points, conventions
- `docs/` scaffold — knowledge base structure per `references/docs-scaffold.md`

**Design principle:** Prefer stable, well-documented dependencies with good training set coverage. Avoid "magic" libraries.

Read full prompt: `references/architect-prompt.md`

---

## Phase 2: Tech Lead Agent

**When to spawn:** After user explicitly approves `ARCHITECTURE.md`.

**Provide to agent:** Approved architecture summary + PRD acceptance criteria.

**Expected output:** `IMPLEMENTATION_PLAN.md` with sequential phases, each containing: files to create, contracts to implement, Definition of Done (`{{TEST_COMMAND}}` / `{{BUILD_COMMAND}}`), Decision Log (chose X over Y because...), PRD coverage per phase.

Read full prompt: `references/tech-lead-prompt.md`

---

## Phase 3: Developer + Review Loop

**When to spawn:** After user explicitly approves `IMPLEMENTATION_PLAN.md`.

**Per plan phase:**
1. Spawn Developer for current phase only (constraint: STOP after this phase)
2. Developer performs self-review loop: verify → self-fix → re-verify until clean
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

**Provide to agent:** `PRD.md` (full) + all project source code.

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
| PRD approved | `[phase-0] PRD: {project}` | `PRD.md` |
| Architecture approved | `[phase-1] architecture: {project}` | `ARCHITECTURE.md`, `AGENTS.md`, `docs/` |
| Plan approved | `[phase-2] plan: {project}` | `IMPLEMENTATION_PLAN.md` |
| Coding phase N passes review | `[phase-3.N] implement: {phase name}` | All phase files |
| Developer fix after review | `[phase-3.N] fix: {issue summary}` | Changed files |
| QA passes | `[phase-4] QA validation passed` | Test files if any |

Rules:
- Use `git add <specific files>` — never `git add .` or `git add -A`
- Commit message must be a single line, no body
- Do NOT push until all phases complete (push only at Finish)

---

## Stop Conditions

| Gate | Trigger | Action |
|------|---------|--------|
| After Phase 0b | `PRD.md` produced | Show to user. Wait for approval. |
| After Phase 1 | `ARCHITECTURE.md` produced | Show to user. Wait for approval. |
| After Phase 2 | `IMPLEMENTATION_PLAN.md` produced | Show to user. Wait for approval. |
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
- CI is **informational, not blocking** — user decides whether to merge despite failures

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
