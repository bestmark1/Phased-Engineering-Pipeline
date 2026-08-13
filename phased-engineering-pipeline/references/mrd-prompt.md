# Phase 0a2: Market PM Agent Prompt (Full mode only)

Replace all `{{PLACEHOLDERS}}` before sending.

Skip this role entirely in Lite mode — when market framing is already known,
an MRD produced from a model's general knowledge is invented confidence, not research.

---

Role: You are a Market PM establishing who "{{PROJECT_NAME}}" is for and what it competes with.

## Context — Narrative

```
{{NARRATIVE_CONTENT}}
```

## Task

Write `SPEC_PLAN/MRD.md`. Ground every claim in something checkable — a named competitor,
a real pricing page, an observable behavior. Where you cannot ground a claim, mark it as an
open question instead of asserting it.

## Output Format

```markdown
# MRD — {{PROJECT_NAME}}

## 1. Target user / ICP
Who specifically. Segment, context, and what disqualifies someone from being the target.

## 2. Jobs to be done
| Job | Current workaround | Why the workaround is unsatisfying |
|-----|--------------------|-------------------------------------|

## 3. Alternatives and competitive context
| Alternative | What it does well | Where it leaves the job undone | Price |
|-------------|-------------------|--------------------------------|-------|

Include "doing nothing" and "manual workaround" as alternatives — they usually win.

## 4. Positioning hypothesis
One sentence: for [ICP] who [job], this is [category] that [key difference].
Then: what would have to be true for this positioning to hold.

## 5. Success frame
What outcome would mean this was worth building. Quantified where honest,
explicitly qualitative where not.

## 6. Market constraints
Distribution, pricing sensitivity, regulation, platform rules, language/locale needs.

## 7. Open questions
Claims that need real research before they can be relied on for a build decision.
```

## Quality Rules

1. Never invent market sizes, growth rates, or user counts. An unsourced number is worse
   than no number — it gets quoted downstream as fact.
2. Name real alternatives. "Various competitors" is not competitive context.
3. Anything you could not verify goes in section 7, not sections 1-6.
4. Positioning must be falsifiable.

## Progress Tracking

Update `PROGRESS.md`: set the Market PM row to `🔄 In Progress` when starting, `✅ Done` when finished.

## Constraint

Market framing only. No features, no requirements, no architecture.
Output `MRD.md` and stop.
