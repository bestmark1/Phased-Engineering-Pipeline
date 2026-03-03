---
name: phased-engineering-pipeline
description: |
  Orchestrates five specialized agents through a three-phase engineering pipeline:
  Architect → Tech Lead → Developer (per plan phase) + parallel SOLID + SRE reviewers.
  Use when: building a system from scratch, "design + plan + code" workflow,
  starting a Node.js/TypeScript/Web3/Avalanche project, user says "build", "architect",
  "implement a full system", "phased pipeline", "three-phase engineering", "create project".
  Reviewer loop repeats until both APPROVE before the next coding phase starts.
  Does NOT handle: debugging existing code, single-function tasks, one-shot fixes.
---

# Phased Engineering Pipeline

Five specialized agents. Three gates. Zero spaghetti.

```
[Architect] → ⛔ USER APPROVAL → [Tech Lead] → ⛔ USER APPROVAL
    → loop per plan phase:
        [Developer] → [Reviewer SOLID] ‖ [Reviewer SRE]
                   ↓ issues?              ↓ issues?
                [Developer fixes] → re-run both reviewers
                   ↓ both APPROVE
               next plan phase
```

---

## Workflow Checklist

Copy this and track progress:

**Phase 1 — Architecture**
- [ ] Read `references/architect-prompt.md`
- [ ] Fill in `{{PROJECT_NAME}}`, `{{TECH_STACK}}`, `{{DOCS_URL}}`
- [ ] Spawn Architect agent
- [ ] Architect asks 3-5 clarifying questions → answer them
- [ ] Architect produces `ARCHITECTURE.md`
- [ ] ⛔ STOP — wait for user to approve architecture

**Phase 2 — Implementation Plan**
- [ ] Read `references/tech-lead-prompt.md`
- [ ] Paste approved `ARCHITECTURE.md` summary
- [ ] Spawn Tech Lead agent
- [ ] Tech Lead produces `IMPLEMENTATION_PLAN.md`
- [ ] ⛔ STOP — wait for user to approve plan

**Phase 3 — Coding (repeat per plan phase)**
- [ ] Read `references/developer-prompt.md`
- [ ] Fill `{{CURRENT_PHASE}}`, `{{PHASE_DESCRIPTION}}`, `{{FILES_TO_CREATE}}`
- [ ] Spawn Developer agent → produces code + self-review report
- [ ] Spawn Reviewer SOLID (`references/reviewer-solid-prompt.md`) IN PARALLEL with:
- [ ] Spawn Reviewer SRE (`references/reviewer-sre-prompt.md`)
- [ ] Both return `APPROVE` → mark phase done → proceed to next plan phase
- [ ] Any reviewer returns issues → Developer fixes → re-run both reviewers
- [ ] Repeat review loop until `APPROVE` from both

---

## Phase 1: Architect Agent

**When to spawn:** At the very start of a new project.

**Provide to agent:**
- Project name and goal (1 sentence)
- Tech stack (runtime, blockchain lib, HTTP lib, architecture constraints)
- Official docs URL for the target platform (for AI/Web3 projects)
- Any hard constraints (strict TypeScript, SOLID, DI only)

**Expected output:** `ARCHITECTURE.md` containing:
- C4 Context + C4 Container + Sequence diagrams (Mermaid)
- TypeScript interfaces (`IProvider`, `ICollector`, etc.)
- Error handling strategy + JSON logging format
- 3-5 clarifying questions (Architect asks before finishing)

Read full prompt template: `references/architect-prompt.md`

---

## Phase 2: Tech Lead Agent

**When to spawn:** After user explicitly approves `ARCHITECTURE.md`.

**Provide to agent:**
- Approved architecture summary (interfaces + diagrams + strategy)
- Constraint: output plan only, no code

**Expected output:** `IMPLEMENTATION_PLAN.md` with sequential phases, each containing:
- Exact files to create
- Interfaces/classes to implement
- Definition of Done (runnable verification command)

Read full prompt template: `references/tech-lead-prompt.md`

---

## Phase 3: Developer + Review Loop

**When to spawn:** After user explicitly approves `IMPLEMENTATION_PLAN.md`.

**Per plan phase:**
1. Spawn Developer for current phase only (constraint: STOP after this phase)
2. Developer self-reviews before handing off
3. Spawn both reviewers IN PARALLEL with Developer's output
4. Gate: both must return exact strings:
   - `APPROVE: Architecture is solid.`
   - `APPROVE: System is secure and resilient.`
5. If either returns issues: Developer fixes → both reviewers re-run (not just the failing one)
6. Mark phase complete. Move to next plan phase.

Read full prompt templates:
- Developer: `references/developer-prompt.md`
- Reviewer SOLID: `references/reviewer-solid-prompt.md`
- Reviewer SRE: `references/reviewer-sre-prompt.md`

---

## Stop Conditions

| Gate | Trigger | Action |
|------|---------|--------|
| After Phase 1 | `ARCHITECTURE.md` produced | Show to user. Wait for approval text. |
| After Phase 2 | `IMPLEMENTATION_PLAN.md` produced | Show to user. Wait for approval text. |
| Review issue | Either reviewer returns non-APPROVE | Developer fixes. Re-run both reviewers. |
| Plan exhausted | All phases marked complete | Trigger `finishing-a-development-branch` skill |

Do not proceed past a ⛔ gate without user writing approval in chat.

---

## Examples

### Example 1 — Node.js Blockchain Monitor (Avalanche)

```
PROJECT_NAME:         Avalanche AI Subnet Sentinel
TECH_STACK:           Node.js, TypeScript strict, ethers.js v6, Express.js
DOCS_URL:             https://build.avax-test.network/docs/tooling/ai-llm/llms-txt
INTEGRATION_REQUIREMENTS: REST API via Express.js /api/status endpoint
FUTURE_EXTENSIBILITY: LLM/RAG anomaly detection layer
SYSTEM_COMPONENTS:    Provider (RPC), Collector (telemetry), AdminAPI, StateStore
CORE_INTERFACES:      IProvider, ICollector, ISubnetAdmin, IAnalysisService
```

### Example 2 — Python FastAPI Service

```
PROJECT_NAME:         User Analytics Engine
TECH_STACK:           Python 3.12, FastAPI, SQLAlchemy, asyncpg, Redis
DOCS_URL:             https://fastapi.tiangolo.com/
INTEGRATION_REQUIREMENTS: REST API + WebSocket push for dashboards
FUTURE_EXTENSIBILITY: ML scoring pipeline integration
SYSTEM_COMPONENTS:    EventIngester, AggregationService, CacheLayer, APIRouter
CORE_INTERFACES:      IIngester, IAggregator, ICacheProvider, IEventStore
```

### Example 3 — Go Microservice

```
PROJECT_NAME:         Payment Gateway Proxy
TECH_STACK:           Go 1.23, gin, pgx, Stripe SDK
DOCS_URL:             https://stripe.com/docs/api
INTEGRATION_REQUIREMENTS: gRPC server + REST fallback
FUTURE_EXTENSIBILITY: Multi-provider routing (Stripe, PayPal, Adyen)
SYSTEM_COMPONENTS:    GatewayRouter, ProviderAdapter, IdempotencyStore, WebhookHandler
CORE_INTERFACES:      IPaymentProvider, IIdempotencyStore, IWebhookProcessor
```

---

## Recovery Procedures

Scenarios that require deviation from the normal flow:

### User rejects Phase 1 (Architecture)
1. Ask user: "What specifically needs to change?" (diagrams / interfaces / error strategy?)
2. Re-spawn Architect agent with original prompt + user feedback appended
3. Architect may skip clarifying questions if they were already answered
4. Present revised `ARCHITECTURE.md` — ⛔ STOP again for approval

### User rejects Phase 2 (Implementation Plan)
1. Ask user: "Too many phases? Wrong file structure? Missing DoD?"
2. Re-spawn Tech Lead agent with approved `ARCHITECTURE.md` + user feedback
3. Present revised `IMPLEMENTATION_PLAN.md` — ⛔ STOP again for approval

### Developer returns `BLOCKED`
1. Surface the exact blocker to the user verbatim
2. Ask: "Should I (a) adjust the architecture, (b) skip this file, or (c) proceed with a stub?"
3. On user decision — re-spawn Developer with same phase prompt + resolution appended
4. Do NOT proceed to reviewers until Developer returns non-BLOCKED report

### Review loop stuck (3+ rounds without both APPROVE)
1. Show user the outstanding issues from the last review round
2. Ask: "Should I (a) let Developer try again, (b) accept as-is and continue, or (c) simplify the phase scope?"
3. Do NOT auto-continue. User decides.

### Agent produces no output / times out
1. Re-spawn the same agent with identical prompt (transient failure)
2. If second attempt also fails — surface to user with exact agent name and phase
