# PROGRESS.md template

The Architect creates `PROGRESS.md` from this template. Every later role updates its own row.

The Architect creates this file; every later role updates its own row. Status values are
`⬜ Not started`, `🔄 In Progress`, `✅ Done`, `⛔ Blocked`.

```markdown
# Progress — {{PROJECT_NAME}}

Pipeline mode: {{PIPELINE_MODE}} · Strict mode: {{STRICT_MODE}}

| Phase | Role | Artifact | Status | Updated |
|-------|------|----------|--------|---------|
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

Report-only until a baseline exists — never a gate.

| Phase | Tokens in/out | Duration | Approx. cost | Review round-trips |
|-------|---------------|----------|--------------|--------------------|

## Blockers

| Date | Phase | Blocker | Owner decision needed |
|------|-------|---------|-----------------------|
```

The Architect pre-fills rows `3.1`–`3.N` as placeholders; the Tech Lead replaces them with
the real phases once `IMPLEMENTATION_PLAN.md` exists.

