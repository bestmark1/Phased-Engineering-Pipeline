# Project Knowledge Base Scaffold

The Architect creates this directory structure after Phase 1.
Subsequent agents populate it throughout the pipeline.

## Structure

This is the **single canonical definition** of the `docs/` tree. `SKILL.md` points here;
do not maintain a second version of this structure anywhere else.

```
docs/
├── README.md                 # Index of the knowledge base (created by Architect)
├── EXECUTION_RULES.md        # How work is executed in this project (Architect)
├── surprises.md              # Project-specific surprises only (Developer/Reviewers)
├── tech-debt-tracker.md      # Known debt items (Developer/Reviewers)
├── QUALITY_SCORE.md          # Domain/layer quality grades (QA)
├── decisions/
│   └── index.md              # Catalog of design decisions
├── exec-plans/
│   ├── active/               # Current IMPLEMENTATION_PLAN.md (symlink or copy)
│   └── completed/            # Archived plans after merge
├── references/
│   └── {tool}-llms.txt       # Distilled vendor docs (created by Analyst)
└── archive/                  # Superseded detail moved out during restructures
```

Create a directory when its first file is written, not upfront — an empty folder tree is
noise an agent has to scan past.

## File Templates

### docs/decisions/index.md

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

### docs/surprises.md

```markdown
# Surprises — {{PROJECT_NAME}}

Only facts an agent CANNOT derive from general knowledge:
strange decisions, workarounds, non-obvious constraints, historical reasons,
dangerous places, local agreements.

Do NOT explain what a framework, database, or HTTP is — that is general knowledge.
A good entry answers: "what is non-standard here, and what breaks the next session
if it doesn't know this?"

| Date | Phase | Surprise | Why it matters |
|------|-------|----------|----------------|
```

### docs/QUALITY_SCORE.md

```markdown
# Quality Score — {{PROJECT_NAME}}

Updated by QA agent after each validation pass.

| Domain / Layer | Coverage | Gaps | Last Checked |
|----------------|----------|------|--------------|
```

## Usage

- **Architect** creates the scaffold and `SPEC_PLAN/CONSTITUTION.md`
- **Analyst** saves distilled docs to `docs/references/{tool}-llms.txt`
- **Developer** appends to `docs/tech-debt-tracker.md` when deferring
- **Developer** appends to `docs/surprises.md` when hitting non-obvious behavior, workarounds, or hidden constraints
- **Reviewers** append to `docs/tech-debt-tracker.md` when flagging non-critical issues
- **Reviewers** append to `docs/surprises.md` when a finding reveals a project-specific trap
- **QA** updates `docs/QUALITY_SCORE.md` after validation
- **Tech Lead** moves completed plans to `docs/exec-plans/completed/` after merge

---

## Documentation restructure policy

Agents must preserve navigability.

Trigger a restructure proposal when:
- a file becomes too long to scan comfortably,
- a file mixes product + architecture + delivery concerns,
- the root index no longer reflects the actual docs tree,
- multiple documents duplicate the same source of truth.

Preferred actions:
1. Split by concern.
2. Keep the parent file as summary + links.
3. Move old detail into `docs/archive/`.
4. Update `PROJECT_INDEX.md`.
5. Record the restructure in `HANDOFF.md` and `PROGRESS.md`.

Agents may propose restructure proactively.
Agents must not silently change canonical meaning during restructure.

