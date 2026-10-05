# Migration: phased-engineering-pipeline → two skills

Design: `docs/plans/2026-10-05-split-pipelines-design.md`, D9. Executed after this repository
change is merged. Steps 3–5 write outside this repository and need the owner's go-ahead.

## 1. Backup (done 2026-10-05)

`~/.claude/skill-backups/phased-engineering-pipeline-2026-10-05.tgz` — full copy of the
installed skill directory. The installation is this repository's clone; it had no local
modifications (`git status` clean at `fe714f8`).

## 2. Behavior in this phase

Phase 1 is a restructure: role prompts, gate policy, validator and receipts (schema v1) are
unchanged. `full`/`lite` became new-product-pipeline, `brownfield` became
existing-system-pipeline. Accepted phases, PROGRESS/HANDOFF and receipts stay valid as history;
artifact paths (`SPEC_PLAN/`, `PROGRESS.md`, `HANDOFF.md`) do not change.

## 3. Installation switch

The old skill is the clone at `~/.claude/skills/phased-engineering-pipeline`. After merge,
pulling it removes its top-level SKILL.md, so the old skill disappears on its own.

1. Move the clone out of the skill root (e.g. `~/Documents/AI_projects/Phased-Engineering-Pipeline`),
   so the host does not scan a repository as a skill.
2. Install both packages from `dist/` into new empty directories (README, "Install / update").

## 4. References to the old name (found 2026-10-05)

| Location | Reference | Action |
|---|---|---|
| `~/.claude/commands/phased-engineering-pipeline.md` | slash command invoking the skill | replace with two commands or retarget |
| `~/.claude/skills/web-pipeline/SKILL.md:7` | "use phased-engineering-pipeline instead" | → new-product-pipeline / existing-system-pipeline |
| `~/.claude/skills/quick-slides/SKILL.md:129` | routing table | same |
| `~/.claude/skills/ai-agent-pipeline/SKILL.md:9,26` | routing text | same |
| `~/.claude/skills/ai-agent-pipeline/references/multi-agent-mode.md:118` | escalation target | same |
| `~/.claude/skills/ai-agent-pipeline/evals/evals.json:50` | `suggest_instead` | same; re-run that skill's evals |
| `~/.claude/projects/-Users-bestmark1-Documents-AI-projects-Empty/memory/project_pipeline_repo_structure.md` | project memory | update repo layout |
| `~/.claude/projects/-Users-bestmark1-Documents-AI-projects-translator-app/memory/harness-workflow.md`, `nextjs-agent-template.md` | project memory | update name |

Telemetry files that mention the name are logs, not references; leave them.

## 5. Active projects

Classify by the selection table in each SKILL.md (design D2), not by the old mode name.

| Project | State found | Target |
|---|---|---|
| Trend watching | `SPEC_PLAN/` with Narrative, MRD, PRD, architecture, plan (Full) | decided with the owner at the next run there; no executable specs yet, so after phase 2 it qualifies for existing-system-pipeline |
