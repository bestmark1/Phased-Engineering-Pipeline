# PROGRESS.md template

The coordinator initializes this file before Product/research, preserving existing state.
Roles may mark In Progress and attach evidence; only the coordinator marks Done after
the required gates and approvals, validated against the approved plan.
Statuses: `⬜ Not started`, `🔄 In Progress`, `✅ Done`, `⛔ Blocked`.

```markdown
# Progress — {{PROJECT_NAME}}

Pipeline mode: {{PIPELINE_MODE}} · Strict mode: {{STRICT_MODE}}

| Phase | Role | Artifact | Status | Updated |
|-------|------|----------|--------|---------|
| 0a | Archaeology (brownfield only) | SPEC_PLAN/archaeology-report.md | ⬜ | |
| research | Domain Analyst (if needed) | domain notes | ⬜ | |
| 0 | Product | Narrative.md + MRD.md (Full) + PRD.md | ⬜ | |
| 0c | Consistency (product) | SPEC_PLAN/clarification-report.md | ⬜ | |
| 1 | Architect | SPEC_PLAN/ARCHITECTURE.md | ⬜ | |
| 2 | Tech Lead | SPEC_PLAN/IMPLEMENTATION_PLAN.md | ⬜ | |
| 2a | Consistency (full) | SPEC_PLAN/cross-artifact-analysis.md | ⬜ | |
| 3.1 | Developer | <phase 1 scope> | ⬜ | |
| 3.N | Developer | <phase N scope> | ⬜ | |
| 4 | QA & Release | QA + release report | ⬜ | |
| 5 | Retro | AGENTS.md / docs updates | ⬜ | |

## Run cost per phase

Record available telemetry only; unknown stays unavailable. Suggested thresholds are
advisory until calibrated; explicit owner budgets still apply.

| Phase | Tokens in/out | Duration | Approx. cost | Review round-trips |
|-------|---------------|----------|--------------|--------------------|

## Blockers

| Date | Phase | Blocker | Owner decision needed |
|------|-------|---------|-----------------------|
```

Tech Lead replaces 3.x placeholders with actual phases. Omit optional rows only with a
recorded n/a reason. Link each completed row to its gate receipt and applicable approval.
Product completion includes owner approval + product consistency; plan completion includes
owner approval + full consistency. Reused artifacts include approval provenance, not a
new approval request for unchanged decisions. Ready for review is still In Progress.
