# phased-engineering-pipeline

> Claude Code skill that orchestrates five specialized agents through a three-phase engineering pipeline: **Architect → Tech Lead → Developer** with parallel SOLID and SRE code reviewers.

---

## What it does

Instead of asking Claude to "build a system" and hoping for the best, this skill enforces a professional engineering workflow with hard approval gates between phases:

```
[Architect] → ⛔ USER APPROVAL → [Tech Lead] → ⛔ USER APPROVAL
    → loop per plan phase:
        [Developer] → [Reviewer SOLID] ‖ [Reviewer SRE]
                   ↓ issues?
                [Developer fixes] → re-run both reviewers
                   ↓ both APPROVE
               next plan phase
```

**Phase 1 — Architecture** — A Senior Architect reads the official docs, asks you 3–5 clarifying questions, then produces `ARCHITECTURE.md` with C4 diagrams (Mermaid), TypeScript interfaces, error handling strategy, and JSON logging format.

**Phase 2 — Implementation Plan** — A Tech Lead converts the approved architecture into a sequential `IMPLEMENTATION_PLAN.md` with exact files, interfaces, and a runnable Definition of Done per phase.

**Phase 3 — Coding loop** — For each plan phase: a Senior Developer implements only that phase, then two reviewers run **in parallel**:
- **Reviewer SOLID** — checks architecture, DI, type strictness, naming
- **Reviewer SRE** — checks resilience, error boundaries, security (ReDoS), resource leaks

Both must return `APPROVE` before the next phase starts. If either returns issues, the developer fixes and both reviewers re-run.

---

## Installation

```bash
# Option A — from .skill file
unzip phased-engineering-pipeline.skill -d ~/.claude/skills/

# Option B — manual
git clone <this-repo>
cp -r phased-engineering-pipeline ~/.claude/skills/
```

---

## Usage

Claude Code activates this skill automatically when you say things like:

```
Build a Node.js monitoring system for Avalanche Subnet
```
```
Architect and implement a FastAPI analytics service
```
```
Create project: Payment Gateway Proxy in Go
```

Or trigger explicitly: `/phased-engineering-pipeline`

---

## Filling in the placeholders

When the skill activates, fill in these values before spawning the Architect agent:

| Placeholder | Example |
|-------------|---------|
| `{{PROJECT_NAME}}` | `Avalanche AI Subnet Sentinel` |
| `{{TECH_STACK}}` | `Node.js, TypeScript strict, ethers.js v6` |
| `{{DOCS_URL}}` | `https://build.avax-test.network/docs/...` |
| `{{INTEGRATION_REQUIREMENTS}}` | `REST API via Express.js` |
| `{{FUTURE_EXTENSIBILITY}}` | `LLM/RAG anomaly detection` |
| `{{SYSTEM_COMPONENTS}}` | `Provider, Collector, AdminAPI, StateStore` |
| `{{CORE_INTERFACES}}` | `IProvider, ICollector, ISubnetAdmin` |

---

## File structure

```
phased-engineering-pipeline/
├── SKILL.md                         # Entry point (199 lines)
└── references/
    ├── architect-prompt.md          # Phase 1: Senior System Architect
    ├── tech-lead-prompt.md          # Phase 2: Tech Lead
    ├── developer-prompt.md          # Phase 3: Senior Backend Developer
    ├── reviewer-solid-prompt.md     # Reviewer: Principal Staff Engineer (SOLID)
    └── reviewer-sre-prompt.md       # Reviewer: SRE & Security Auditor
```

---

## Recovery procedures

| Scenario | What happens |
|----------|-------------|
| User rejects Architecture | Re-spawn Architect with feedback, new approval gate |
| User rejects Plan | Re-spawn Tech Lead with feedback, new approval gate |
| Developer returns `BLOCKED` | Surface blocker to user, wait for decision |
| Review loop stuck 3+ rounds | Escalate to user: retry / accept / simplify scope |
| Agent timeout | Re-spawn once, then escalate |

---

## Q-Standard score

Evaluated against the [Universal Skills Quality Standard](https://github.com/shanraisshan/claude-code-best-practice):

| Dimension | Score |
|-----------|-------|
| Structural Compliance | 20/20 |
| Description Quality | 20/20 |
| Instruction Density | 18/20 |
| Completeness | 19/20 |
| Runtime Performance | 18/20 |
| **Total** | **95/100 (A)** |

---

## Supported stacks

Works with any stack — placeholders are generic. Tested examples:

- **Node.js + TypeScript + ethers.js** (Avalanche/Web3 monitoring)
- **Python + FastAPI + SQLAlchemy** (analytics services)
- **Go + gin + pgx** (microservices)

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Claude Code skills support (`~/.claude/skills/`)
