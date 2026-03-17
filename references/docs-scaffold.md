# Project Knowledge Base Scaffold

The Architect creates this directory structure after Phase 1.
Subsequent agents populate it throughout the pipeline.

## Structure

```
docs/
├── design-docs/
│   └── index.md              # Catalog of design decisions
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

- **Architect** creates the scaffold and `CONSTITUTION.md` (project root)
- **Analyst** saves distilled docs to `docs/references/{tool}-llms.txt`
- **Developer** appends to `docs/tech-debt-tracker.md` when deferring
- **Reviewers** append to `docs/tech-debt-tracker.md` when flagging non-critical issues
- **QA** updates `docs/QUALITY_SCORE.md` after validation
- **Tech Lead** moves completed plans to `docs/exec-plans/completed/` after merge
