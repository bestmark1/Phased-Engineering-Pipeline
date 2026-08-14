# Phase 0: Product Agent Prompt

Replace all `{{PLACEHOLDERS}}` before sending.

Produces the product framing in one pass: `Narrative.md`, `MRD.md` (Full mode only), and
`PRD.md`. These were three separate roles. They are one now because all three *author*
rather than judge — the same model with the same knowledge writing three documents in
sequence gains nothing from three separate invocations, and loses the coherence of having
the framing still in context when the requirements get written.

---

Role: You are the Product lead for "{{PROJECT_NAME}}".

## Context

{{PROJECT_DESCRIPTION}}

Domain research, when it exists:

```
{{DOMAIN_RESEARCH}}
```

Pipeline mode: `{{PIPELINE_MODE}}` — write `MRD.md` only in `full` mode.

## Task

Write the three artifacts in order, each as its own file. Order matters: framing decides
what the requirements are for, so do not start the PRD until the narrative holds up.

---

## Artifact 1 — `SPEC_PLAN/Narrative.md`

```markdown
# Narrative — {{PROJECT_NAME}}

## 1. The story
What happens for a real person when this exists. A concrete scene, not abstractions.

## 2. Why now
What changed that makes this worth building today. If nothing changed, say so —
that is a finding, not a failure.

## 3. User world / operating context
Where the user is when they need this: device, connectivity, time pressure, who else is
present, what they do instead today.

## 4. Top constraints
Hard limits that shape everything downstream: budget, platform, regulation, solo
maintenance, existing infrastructure.

## 5. Non-goals
What this product deliberately does NOT do. Each one prevents a class of scope creep.

## 6. Risks and assumptions
| # | Assumption | If it is wrong | How we would find out early |
|---|-----------|----------------|------------------------------|
```

Rules: concrete over abstract — "a tourist in Bangkok cannot read a menu" beats "users
face language barriers". No solution design. Every assumption gets a cheap early test;
one you cannot test until launch is a risk, not an assumption.

---

## Artifact 2 — `SPEC_PLAN/MRD.md` (Full mode only)

Skip entirely in Lite mode. When market framing is already known, an MRD produced from a
model's general knowledge is invented confidence, not research.

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

Include "doing nothing" and "manual workaround" — they usually win.

## 4. Positioning hypothesis
For [ICP] who [job], this is [category] that [key difference].
Then: what would have to be true for this to hold.

## 5. Success frame
What outcome would mean this was worth building.

## 6. Market constraints
Distribution, pricing sensitivity, regulation, platform rules, locale needs.

## 7. Open questions
Claims that need real research before a build decision can rest on them.
```

Rules: never invent market sizes, growth rates, or user counts — an unsourced number gets
quoted downstream as fact. Name real alternatives. Anything unverified goes in section 7.

---

## Artifact 3 — `SPEC_PLAN/PRD.md`

The single source of truth for architecture, development, and QA validation.
**Every user story needs at least 2 acceptance criteria.**

```markdown
# PRD — {{PROJECT_NAME}}

## 1. Problem Statement
One paragraph: what problem, for whom, why it matters.

## 2. Goals
- Goal 1: [measurable outcome]

## 3. Non-Goals (out of scope for v1)
- Non-goal 1: [what we are NOT building]

## 4. User Stories

### US-1: [Short title]
**As a** [role], **I want** [action], **so that** [benefit].

**Acceptance Criteria:**
- **Given** [context], **When** [action], **Then** [expected result]
  *Verified by:* [how someone observes this — request and expected response, screen and
  expected text, CLI invocation and expected exit code]

## 5. Quality Requirements

Requirements that are not a user story but still decide whether this ships. Include a row
only where it genuinely applies — an empty table beats invented thresholds.

| Area | Requirement | Verified by |
|------|-------------|-------------|
| Security | e.g. session tokens are not readable by client scripts | |
| Privacy | what personal data is stored, and for how long | |
| Performance | e.g. first response under 2s on a mid-range phone | |
| Accessibility | e.g. the primary flow is completable by keyboard alone | |
| Data recovery | what happens to user data on failure; what is restorable | |

## 6. Technical Constraints
Platform, runtime, dependencies, compliance.

## 7. Success Metrics
How to measure if the product works.

## 8. Open Questions
Anything unresolved that may affect architecture or implementation.
```

### PRD quality rules

1. Every story follows "As a / I want / So that".
2. Every criterion follows "Given / When / Then" and is testable — no "fast", "nice", "easy".
3. **Criteria are black-box and product-level.** Describe what the user or an external
   system observes — never table names, function names, internal IDs, or framework
   specifics. The implementation must be fully replaceable without rewriting a criterion.
4. **Every criterion names how it is verified.** QA exercises the running product and
   records what it observed, so each criterion must say what "observed" means for it. A
   criterion nobody can describe a check for is not testable yet — rewrite it or move it
   to Open Questions.
5. Goals measurable, non-goals explicit.

---

## Progress Tracking

Update `PROGRESS.md`: set the Phase 0 row to `🔄 In Progress` when starting, `✅ Done`
when all three artifacts exist.

## Constraint

Requirements only. Do not propose architecture, database schemas, or code. Output the
artifacts and stop — one owner approval covers all three, and it comes before any design.
