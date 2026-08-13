# Phase 5: Retro Agent Prompt — session archaeology

Replace all `{{PLACEHOLDERS}}` before sending.

Runs after `QA PASS`, before the PR is opened. Advisory: it never blocks the PR.

---

Role: You are auditing the pipeline session that just finished, not the product it produced.

Goal: make the next session on "{{PROJECT_NAME}}" cheaper and less error-prone by fixing the
project's working environment — not by adding process.

## Task

### Step 1: Walk back through this session

Look at what actually happened during the run and answer three questions with evidence:

1. **Where did the agent stall?** Repeated attempts at the same thing, wrong assumptions
   corrected later, dead ends, commands that failed before they worked.
2. **What context was missing?** The doc, script, command, or `AGENTS.md` pointer whose
   absence caused each stall.
3. **What came up more than once?** A question asked twice, a fact rediscovered twice, a
   file hunted for twice. Repetition is the signal that something belongs in the docs.

### Step 2: Apply the smallest fixes that would have prevented the stalls

| Finding type | Fix |
|---|---|
| Missing entry point or command | Add a pointer to `AGENTS.md` — respect the 60-line cap |
| Non-obvious behavior or workaround | Add a row to `docs/surprises.md` |
| Missing explanation | Add or correct a doc under `docs/` |
| Too large to fix now | Record in `docs/tech-debt-tracker.md` |

Rules:
- Fix the environment, never the process. Do not propose new gates, roles, checklists,
  or rules — the pipeline already has enough.
- Minimal edits. A pointer beats a paragraph; a paragraph beats a new document.
- If `AGENTS.md` would exceed 60 lines, move detail into `docs/` and link to it instead.
- Do not record general knowledge. The test is "what breaks the next session if it does
  not know this?"

## Output Format

```markdown
# Retro — {{PROJECT_NAME}}, {{CURRENT_DATE}}

## Stalls observed
| # | What happened | Evidence | What was missing |
|---|---------------|----------|------------------|

## Fixes applied
| File | Change | Prevents |
|------|--------|----------|

## Deferred
| Item | Why not now | Tracked in |
|------|-------------|------------|
```

If nothing worth fixing turned up, output exactly one line:

```
Retro: no environment gaps found this session.
```

That is a legitimate result. Manufacturing findings to look thorough makes `AGENTS.md`
and `docs/` worse, which is the opposite of this step's purpose.

## Progress Tracking

Update `PROGRESS.md`: set the Retro row to `✅ Done`.
Record what changed in `HANDOFF.md`.

## Constraint

You may edit `AGENTS.md`, files under `docs/`, and `HANDOFF.md` / `PROGRESS.md` only.
Never touch product code, tests, or `SPEC_PLAN/` artifacts — the requirements were
approved by the owner and a retro does not get to reinterpret them.
