## Changing an approved artifact

Implementation discovers what planning could not know: an API behaves differently than
documented, a requirement is impossible as written, two criteria contradict each other
only once code exists. Without a route for this, an agent either quietly builds something
other than what was approved, or buries the discovery in `tech-debt-tracker.md` and
implements the known-wrong thing. Both produce a product that contradicts its own spec.

**Update the earliest artifact the discovery invalidates, then propagate downstream.**

| What the discovery changes | Earliest artifact to update |
|---|---|
| What the product does for the user | `SPEC_PLAN/PRD.md` |
| A contract, data shape, or dependency direction | `SPEC_PLAN/ARCHITECTURE.md` |
| Only how a phase is built | `SPEC_PLAN/IMPLEMENTATION_PLAN.md` |
| A project rule or convention | `SPEC_PLAN/CONSTITUTION.md` |

Leaving the PRD stale while the code moves on is how a spec quietly becomes fiction.

**Stop and ask the owner** when the change is material: observable behavior, a contract
someone depends on, data retention or deletion, security or permissions, cost, a new
external dependency, or scope nobody asked for. Proceed and record when it is immaterial —
naming, internal structure, a clarification that changes no behavior. When in doubt, treat
it as material: one question costs minutes, an unapproved behavior change found at release
costs the phase.

**Criterion IDs never move.** Rewording a criterion keeps its ID. Splitting one into two
keeps the original ID for the part that retains the intent and appends a new number for
the rest. A criterion that no longer applies is marked in place as
`**AC-014 [RETIRED]** — reason`; its number is never reassigned. Retired criteria stay
visible in the PRD and in the traceability matrix, and drop out of everything that counts:
no phase covers them, no test must prove them, and QA excludes them from coverage and from
the verdict. Renumbering an approved PRD silently
invalidates every test comment, plan entry and QA report that cites it — the references
still parse, they just point somewhere else, which is worse than breaking outright.

Every artifact change gets a line in `HANDOFF.md` — what was discovered, which artifact
changed, whether the owner approved it. A silent edit to an approved document is
indistinguishable from scope creep on review.
