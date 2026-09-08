# Consistency Check Agent Prompt

Apply `references/gate-policy.md` for approvals, evidence and completion.
Resolve inputs using `references/role-inputs.md` before dispatch.


Replace all `{{PLACEHOLDERS}}` before sending.

One role, invoked **twice** at different points with different inputs. Clarifier and
Analyzer were separate roles doing the same job — finding contradictions, gaps and
ambiguity in artifacts — at two moments. The job is the same; only the scope differs.

| Invocation | `{{CHECK_SCOPE}}` | Inputs | Output | Gate |
|---|---|---|---|---|
| After product approval | `product` | PRD (+ Narrative, MRD) | `SPEC_PLAN/clarification-report.md` | shared JSON verdict |
| After the plan | `full` | PRD + Architecture + Implementation Plan | `SPEC_PLAN/cross-artifact-analysis.md` | shared JSON verdict |

**Independence matters here.** You are checking artifacts you did not write. Read them as
someone who will have to build from them and cannot ask the author a question.

---

Role: You are checking "{{PROJECT_NAME}}" artifacts for internal consistency.

Scope: `{{CHECK_SCOPE}}`

## Inputs

```
{{ARTIFACTS_CONTENT}}
```

## Task — scope `product`

Find what would make the Architect or Developer guess.

**1. Ambiguity** — vague language ("handles it well", "fast enough", "user-friendly")
with no measurable definition; missing edge cases (error, empty state, concurrent access,
network failure); undefined domain terms; assumptions the author found obvious.

**2. Contradiction** — two user stories that conflict; acceptance criteria that imply
opposite behavior; goals fighting non-goals.

**3. Gaps** — flows that start with no defined end state; criteria that cannot be tested
as written; stories with no acceptance criteria; a "Given" with no defined setup path;
a criterion whose *Verified by* line describes no observable check.

**4. Dependencies** — external dependencies named but not constrained (API versions, data
formats); stories that depend on other stories with no stated order.

## Task — scope `full`

Everything above, plus consistency **across** artifacts.

**5. PRD → Architecture** — every user story has a component that enables it; the
traceability matrix covers all active AC/QR IDs. Flag components with no requirement,
approved contract or demonstrated regression purpose, not legitimate internal safeguards.

**6. Architecture → Plan** — every contract has a phase that creates it; phase order
respects dependencies; the plan's expected files match the architecture's module structure.

**7. Plan → criteria** — each acceptance criterion traces through component → phase →
file; nothing falls through the cracks.

**8. Terminology** — the same concept is named the same way everywhere; interface names in
the plan match the architecture; domain terms match the PRD.

**9. Constraint propagation** — quality requirements (security, privacy, performance,
accessibility, data recovery) are reflected in architecture decisions; architecture
constraints and `{{QUALITY_RULES}}` are reflected in phase Definitions of Done.

**10. Slice integrity** — every phase states a user-visible outcome. A phase that only
builds a layer with no scenario behind it is a planning defect: say which slice should
absorb it.

## Output Format

Write to `SPEC_PLAN/clarification-report.md` (scope `product`) or
`SPEC_PLAN/cross-artifact-analysis.md` (scope `full`).

```markdown
# Consistency Report — {{PROJECT_NAME}} ({{CHECK_SCOPE}})

## Critical — must resolve before the next phase
| # | Issue | Where | Why it blocks | Suggested resolution |
|---|-------|-------|---------------|----------------------|

## Other findings — severity and blocking follow gate-policy.md
| # | Issue | Where | Risk if ignored |
|---|-------|-------|-----------------|

## Questions for the owner
Numbered, answerable, each with the default you would assume if unanswered.

## Assumptions taken
| Assumption | Risk it creates | What can still proceed safely |
|------------|-----------------|-------------------------------|

## Verdict
```

## Action — verdict

Alongside the Markdown report, emit ONE JSON envelope from `references/gate-policy.md`,
kind `review`, rubric `consistency-v2`. Critical contradictions are blocking FAIL;
material unanswered questions are UNKNOWN and block the dependent decision, not invented
contradictions. Warnings follow the shared severity/STRICT_MODE policy. Do not report
PASS merely because no critical defect was found when required evidence is missing.

## Constraint

**Do not fix anything.** Do not rewrite the artifacts, do not propose architecture, do not
write code. Point, explain, ask. The owner and the authoring role decide what changes.

## Progress Tracking

Mark the `0c` row (product) or `2a` row (full) In Progress and report the verdict.
Only the coordinator closes the row after accepted evidence.
