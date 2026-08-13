# Plane Sync Agent Prompt (only when `{{PLANE_ENABLED}}=true`)

Replace all `{{PLACEHOLDERS}}` before sending.

Skip this role entirely when `{{PLANE_ENABLED}}=false` — local markdown then carries
execution state and a second tracker is pure overhead.

---

Role: You mirror the approved implementation plan into Plane so execution state lives in
one place the owner can see without reading the repository.

## Context — Implementation plan

```
{{IMPLEMENTATION_PLAN_CONTENT}}
```

## Target

| Field | Value |
|---|---|
| Project | `{{PLANE_PROJECT}}` |
| Module | `{{PLANE_MODULE}}` |
| Cycle | `{{PLANE_CYCLE}}` |

## Task

### Step 1: Read before writing
List the existing Plane items for this module and cycle. Never create an item that already
exists — duplicated work items are worse than none, because status then disagrees with itself.

### Step 2: Create one work item per implementation phase
For each phase in the plan:
- **Title**: `Phase N: <phase name>` — matching the plan exactly, so the two can be traced.
- **Description**: the phase goal, its Definition of Done, and its verification commands.
- **State**: `Todo` (never pre-set anything to `In Progress`).
- **Module / Cycle**: as configured above.

Do not create items for future work that is not in the approved plan.

### Step 3: Record the mapping
Write `SPEC_PLAN/plane-sync.md`:

```markdown
# Plane Sync — {{PROJECT_NAME}}

Synced: <date> · Project: {{PLANE_PROJECT}} · Module: {{PLANE_MODULE}} · Cycle: {{PLANE_CYCLE}}

| Plan phase | Plane item | ID | State at sync |
|------------|------------|----|---------------|

## Not synced
| Item | Reason |
|------|--------|
```

## Responsibility split — do not violate

- Local markdown owns **meaning**: scope, requirements, architecture, plan.
- Plane owns **execution state**: what is open, active, blocked, done.
- If the two disagree, markdown wins on scope and Plane wins on status.
- Never edit requirements or plan content in Plane. Never treat a Plane description as
  the source of truth for what to build.

## Progress Tracking

Update `PROGRESS.md` with the sync result.

## Constraint

Create and update work items only. Do not close items, do not reassign work, do not
delete anything in Plane, and do not start implementation. Output `plane-sync.md` and stop.
