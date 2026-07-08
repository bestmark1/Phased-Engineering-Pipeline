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
   → git: commit code
   → [Reviewer SOLID] ‖ [Reviewer SRE]
   → issues? fix → recommit → re-review
   → both APPROVE → update PROGRESS.md / HANDOFF.md / Plane → next phase
→ [QA Agent] → validates PRD acceptance criteria + phase DoD trace
→ issues? → fix → re-validate
→ QA PASS
→ [Retro] → session archaeology → minimal improvements to AGENTS.md / docs
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

6. **Tests are requirements**
   - Every test locks in a PRD acceptance criterion or an architecture constraint,
     and must name it.
   - A test without a requirement freezes an accidental implementation:
     future sessions will maintain the test instead of fixing the approach.
   - Agents may propose tests but must state what requirement each one fixes.

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
| `{{TEST_COMMAND}}` | Test runner | `npm test` |
| `{{LINT_COMMAND}}` | Linter / static analysis | `npm run lint` |
| `{{TYPECHECK_COMMAND}}` | Type checker if separate | `tsc --noEmit` |
| `{{QUALITY_RULES}}` | Stack-specific quality rules | strict TS, no `any`, constructor DI |
| `{{INTERFACE_STYLE}}` | Contract style | TypeScript interfaces |
| `{{DOCS_URL}}` | Official docs URL | `https://nextjs.org/docs` |
| `{{ROLLBACK_COMMAND}}` | How to undo last change | `git revert HEAD` |
| `{{STRICT_MODE}}` | `true` blocks gates, `false` advisory | `true` |
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

Inside `docs/`:
- `README.md`
- `EXECUTION_RULES.md`
- `surprises.md`
- `tech-debt-tracker.md`
- `QUALITY_SCORE.md`
- optional subfolders: `product/`, `architecture/`, `delivery/`, `decisions/`, `archive/`

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

docs/
  README.md
  EXECUTION_RULES.md
  surprises.md
  product/
  architecture/
  delivery/
  decisions/
  tech-debt-tracker.md
  QUALITY_SCORE.md
  archive/
```

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

### 12) QA Agent
Checks:
- PRD acceptance criteria traceability
- test / build / lint / typecheck exit codes
- scope creep
- quality score updates
- remaining phase gaps

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

Rules:
- Never pull tasks from future phases.
- Never change files outside the current phase scope unless:
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
| Basic | exit codes, lint, typecheck, unit tests | every coding phase |
| Medium | integration tests, contract tests, smoke tests | QA |
| High | production logs, metrics, manual checklists | post-deploy, outside this skill |

### Exit-code rules
Any required verification command must return exit code 0.
Non-zero exit code = FAIL.
Agent must not continue through a blocking gate.

## Pre-execution checklist

Before any code changes:
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

## Notes for Plane MCP

Plane MCP Server supports multiple transport methods, including HTTP with OAuth, HTTP with PAT token, and Local Stdio for self-hosted instances. Plane documents setup paths for Claude.ai, Claude Desktop, Cursor, VS Code, and other editors, and states that the MCP server enables agents to interact with Plane project-management capabilities.
