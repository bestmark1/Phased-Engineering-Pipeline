# phased-engineering-pipeline

> Claude Code skill that orchestrates eight specialized agents through a full BMAD engineering pipeline: **Analyst → PM → Architect → Tech Lead → Developer** with parallel SOLID and SRE code reviewers, then **QA validation**. Includes auto git commits, feature branch workflow, and CI/CD awareness.

---

## What it does

Instead of asking Claude to "build a system" and hoping for the best, this skill enforces a professional BMAD engineering workflow with six approval gates:

```
[Analyst] → [PM] → PRD.md → ⛔ USER APPROVAL
  → git: create feature/{slug} branch, commit PRD
  → [Architect] → ARCHITECTURE.md → ⛔ USER APPROVAL → git: commit
    → [Tech Lead] → IMPLEMENTATION_PLAN.md → ⛔ USER APPROVAL → git: commit
      → loop per plan phase:
          [Developer] → git: commit code
          → [Reviewer SOLID] ‖ [Reviewer SRE]
          → both APPROVE → next phase
      → [QA Agent] → validates PRD acceptance criteria
          → QA PASS → git: push → gh pr create → ⛔ USER REVIEWS DIFF
```

**Phase 0a — Domain Analysis** — A Domain Analyst researches the problem space, stakeholders, competitors, and risks. Asks 5-8 clarifying questions.

**Phase 0b — Product Requirements** — A Product Manager converts research into `PRD.md` with user stories (As a / I want / So that), acceptance criteria (Given / When / Then), and success metrics.

**Phase 1 — Architecture** — A Senior Architect reads the official docs, asks 3-5 clarifying questions, then produces `ARCHITECTURE.md` with C4 diagrams (Mermaid), contracts/interfaces, and error handling strategy.

**Phase 2 — Implementation Plan** — A Tech Lead converts the approved architecture into `IMPLEMENTATION_PLAN.md` with exact files, contracts, and a runnable Definition of Done per phase.

**Phase 3 — Coding loop** — For each plan phase: a Senior Developer implements only that phase, auto-commits, then two reviewers run **in parallel**:
- **Reviewer SOLID** — checks architecture, DI, type safety, naming
- **Reviewer SRE** — checks resilience, error boundaries, security, resource leaks

Both must return `APPROVE` before the next phase starts.

**Phase 4 — QA Validation** — A QA Engineer extracts every acceptance criterion from the PRD, traces through code, runs tests/build/lint, detects scope creep. Binary verdict: `QA PASS` or failure list.

**Finish** — Push feature branch, create PR via `gh pr create`, verify CI checks, user reviews diff before merge.

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
| `{{TEST_COMMAND}}` | Test runner | `flutter test` |
| `{{LINT_COMMAND}}` | Static analysis | `flutter analyze` |
| `{{QUALITY_RULES}}` | Language-specific quality rules | null safety, no dynamic, const constructors |
| `{{INTERFACE_STYLE}}` | How contracts are defined | abstract class / mixin |
| `{{DOCS_URL}}` | Official docs URL | https://docs.flutter.dev/ |

**Pre-built stack profiles included:** Flutter/Dart, TypeScript/Node.js, Python/FastAPI, Go.

---

## File structure

```
phased-engineering-pipeline/
├── SKILL.md                         # Entry point (357 lines)
└── references/
    ├── analyst-prompt.md            # Phase 0a: Domain Analyst
    ├── pm-prompt.md                 # Phase 0b: Product Manager → PRD
    ├── architect-prompt.md          # Phase 1: Senior System Architect
    ├── tech-lead-prompt.md          # Phase 2: Tech Lead
    ├── developer-prompt.md          # Phase 3: Senior Developer
    ├── reviewer-solid-prompt.md     # Reviewer: Principal Staff Engineer (SOLID)
    ├── reviewer-sre-prompt.md       # Reviewer: SRE & Security Auditor
    └── qa-prompt.md                 # Phase 4: QA Engineer
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
