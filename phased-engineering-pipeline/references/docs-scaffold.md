# Project Knowledge Base Scaffold

The Architect creates this directory structure after Phase 1.
Subsequent agents populate it throughout the pipeline.

## Structure

```
docs/
├── design-docs/
│   ├── index.md              # Catalog of design decisions
│   └── core-beliefs.md       # Agent-first operating principles for this project
├── exec-plans/
│   ├── active/               # Current IMPLEMENTATION_PLAN.md (symlink or copy)
│   └── completed/            # Archived plans after merge
├── references/
│   └── {tool}-llms.txt       # Distilled vendor docs (created by Analyst)
├── QUALITY_SCORE.md           # Domain/layer quality grades (updated by QA)
└── tech-debt-tracker.md       # Known debt items (updated by Developer/Reviewers)
```

## File Templates

### docs/design-docs/index.md

```markdown
# Design Decisions Index

| # | Decision | Date | Status | Link |
|---|----------|------|--------|------|
| 1 | Initial architecture | YYYY-MM-DD | Active | ARCHITECTURE.md |
```

### docs/design-docs/core-beliefs.md

```markdown
# Core Beliefs — {{PROJECT_NAME}}

Principles that guide agent and human decisions in this project:

1. **Repository is the source of truth** — if it's not in the repo, it doesn't exist
2. **Contracts before implementation** — define interfaces first, implement second
3. **Boring tech wins** — prefer stable, well-documented dependencies
4. **Every story is testable** — no acceptance criterion without a verification path
5. **Debt is tracked, not hidden** — use tech-debt-tracker.md for all deferrals
```

### docs/tech-debt-tracker.md

```markdown
# Tech Debt Tracker

| Date | Phase | Item | Reason | Priority | Status |
|------|-------|------|--------|----------|--------|
```

### docs/QUALITY_SCORE.md

```markdown
# Quality Score — {{PROJECT_NAME}}

Updated by QA agent after each validation pass.

| Domain / Layer | Coverage | Gaps | Last Checked |
|----------------|----------|------|--------------|
```

## Usage

- **Architect** creates the scaffold and populates `design-docs/core-beliefs.md`
- **Analyst** saves distilled docs to `docs/references/{tool}-llms.txt`
- **Developer** appends to `docs/tech-debt-tracker.md` when deferring
- **Reviewers** append to `docs/tech-debt-tracker.md` when flagging non-critical issues
- **QA** updates `docs/QUALITY_SCORE.md` after validation
- **Tech Lead** moves completed plans to `docs/exec-plans/completed/` after merge
