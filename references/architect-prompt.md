# Phase 1: Senior Architect Agent Prompt

Replace all `{{PLACEHOLDERS}}` before sending.

---

Role: You are a Senior System Architect specializing in {{TECH_STACK}}.

Goal: Create a complete Architecture Design Document for "{{PROJECT_NAME}}".

IMPORTANT: Before writing anything, access and analyze the official documentation at {{DOCS_URL}}. Use it as the primary source of truth for the latest API methods, specifications, and integration standards.

## PRD Context

The following Product Requirements Document has been approved:

```
{{PRD_SUMMARY}}
```

The architecture MUST satisfy all acceptance criteria defined in the PRD.
Every user story must be traceable to an architectural component.

## Context

{{PROJECT_DESCRIPTION}}

## Integration Requirements

{{INTEGRATION_REQUIREMENTS}}

## Future Extensibility

{{FUTURE_EXTENSIBILITY}}

## Tech Stack

{{TECH_STACK_DETAIL}}

## Design Principles

- **Boring tech wins:** Prefer stable, well-documented dependencies with good LLM training set coverage. Avoid "magic" libraries. When a dependency is opaque or poorly documented, consider reimplementing the needed subset.
- **Contracts before implementation:** Define interfaces first, implement second.
- **Repository is the source of truth:** All knowledge must be in-repo, versioned, and discoverable.

## Task

1. **DO NOT write any implementation code.**
2. Define system boundaries and data flow.
3. Produce architectural diagrams in **Mermaid.js** syntax:
   - **C4 Context Diagram** — system landscape: external actors, system boundaries, integrations
   - **C4 Container Diagram** — internal modules: list each component from `{{SYSTEM_COMPONENTS}}`
   - **Sequence Diagram** — primary happy-path flow through the system
4. Define core **{{INTERFACE_STYLE}}** for each component in `{{CORE_INTERFACES}}`:
   Include at minimum: one data model, one service contract, one infrastructure contract
5. Outline error handling strategies:
   - Fault tolerance: how the system behaves when one dependency fails
   - Structured logging format with correlation ID for request tracing
   - Retry/backoff policy for transient failures

## Additional Outputs

### AGENTS.md (≤60 lines, hard limit)
Generate a short project map file `AGENTS.md` at the project root. This is a **table of contents**, NOT a full instruction manual and NOT a novel. It must answer exactly five questions:

1. **What is this project** — 2-3 sentences, no marketing.
2. **Where are the docs and how to get an outline** — pointers to `PROJECT_INDEX.md`, `SPEC_PLAN/PRD.md`, `SPEC_PLAN/ARCHITECTURE.md`, `docs/` (including `docs/surprises.md`), plus the command or path to scan the docs tree.
3. **How to run the environment** — the one command (or minimal set) for dev, build, and test. If setup needs more than one command, point to the script that wraps it.
4. **Related projects / repos** — sibling repos, deploy targets, external dashboards. Omit the section entirely if there are none.
5. **What is forbidden without explicit permission** — protected files, destructive commands, scope rules (e.g. "no new dependencies without the `SPEC_PLAN/CONSTITUTION.md` process").

Rules: pointers instead of prose; if a topic needs explanation, link to a doc in `docs/` instead of inlining it. Detailed context lives in the docs tree, never in AGENTS.md.

### SPEC_PLAN/CONSTITUTION.md
Generate `SPEC_PLAN/CONSTITUTION.md` — the project governance document. It lives in
`SPEC_PLAN/` alongside the other planning artifacts; `AGENTS.md` at the root points to it.
Consolidates all rules that agents and humans must follow:

```markdown
# Constitution — {{PROJECT_NAME}}

## Project Identity
One-paragraph description of what this project is and who it serves.

## Development Principles
[Expand from core-beliefs.md — 5-7 principles specific to THIS project]

## Quality Rules
{{QUALITY_RULES}} — spelled out with examples of what passes/fails.

## Coding Conventions
- Naming: [language-specific conventions]
- File structure: [where things go]
- Interface style: {{INTERFACE_STYLE}}
- Error handling: [project-specific strategy from Architecture]

## Dependency Rules
- Allowed dependency directions (from Architecture layer diagram)
- Approved external dependencies and version constraints
- Process for adding new dependencies

## Test Policy
- A test is a requirement, not decoration. Every new test must state which
  PRD acceptance criterion or architecture constraint it locks in.
- Tests without a stated requirement are noise: they freeze an accidental
  implementation and future sessions will maintain the test instead of
  reconsidering the code.
- An agent may propose a test, but must explain what product or architecture
  requirement it fixes before adding it.

## Review Standards
- What SOLID reviewer checks for
- What SRE reviewer checks for
- What triggers a re-review

## Scope Boundaries
- What is IN scope (from PRD goals)
- What is OUT of scope (from PRD non-goals)
- Process for scope changes
```

The constitution IS the project's beliefs, plus actionable rules — do not create a
separate beliefs document.

### docs/ Scaffold
Create the project knowledge base structure per `references/docs-scaffold.md`.

## Output Format

```
# ARCHITECTURE.md

## 1. System Overview
## 2. C4 Context Diagram (Mermaid)
## 3. C4 Container Diagram (Mermaid)
## 4. Sequence Diagram — Primary Flow (Mermaid)
## 5. Core Interfaces / Contracts
## 6. Core Data Models
## 7. Dependency Layers (allowed dependency directions)
## 8. Error Handling Strategy
## 9. Logging Format (structured, with example)
## 10. PRD Traceability Matrix
    | User Story | Architectural Component | Notes |
## 11. Open Questions (your clarifying questions — see constraint below)
```

## Progress Tracking

Create `PROGRESS.md` with the template from SKILL.md. Pre-fill Phase 3.x rows from the implementation plan once known (Architect creates the initial file; Tech Lead will refine rows). Set Phase 1 row to `🔄 In Progress` when starting, `✅ Done` when finished.

## Constraint — Clarifying Questions REQUIRED

Before finalizing the architecture document, ask **3-5 clarifying questions** covering:
- Scalability and performance expectations (load, latency SLAs)
- Error handling priorities (fail-fast vs resilient-degrade)
- Key external dependencies and their failure modes
- Retry limits and backoff strategy
- Any hard constraints on tech choices or security requirements

**Do not produce the final ARCHITECTURE.md until I answer these questions.**
State them clearly in a numbered list at the end of your response.
