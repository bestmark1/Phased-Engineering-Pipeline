# Entry — coordinator steps 0, 2, 3 and OBS decisions

Loaded by the coordinator at the start of every existing-system run, and again when the
characterization slice reports observed behavior for the owner's decision.

## Step 0 — entry (coordinator + owner)

Write only the run state (`STATE_FILE`, default `PROGRESS.md` and `HANDOFF.md`). Ask once, record each answer in `STATE_FILE`:

0. **Where this run's files live.** If the project already uses `specs/` for something else, choose
   another `SPECS_DIR` (e.g. `specs-exec`). If `PROGRESS.md`/`HANDOFF.md` are maintained by other
   workflows or sessions, keep this run's state in `STATE_FILE` = `SPEC_PLAN/initiatives/<id>/PROGRESS.md`
   and its artifacts in `INITIATIVE_DIR` = `SPEC_PLAN/initiatives/<id>/`, and record that choice;
   every later "HANDOFF.md" instruction means `STATE_FILE`.
1. **Permissions:** may the pipeline write `AGENTS.md` and `docs/` here; may it make local commits of
   the run's specs, INDEX and parity files on a working branch (parity needs a committed `suite_sha`); may it push working
   branches (own repository: yes by default; someone else's: ask); who sets up read-only
   access to the database, logs and CI.
2. **Process map:** a short table of the development process — where a mistake is expensive
   (mark red: guardrails and checks first) and where time goes (mark blue: candidates for
   docs, scripts or an eval loop). Automate the overlap of high repetition and low risk;
   put a check in front of high risk.
3. **One scenario:** pick the single most painful scenario for this run. Before proposing it, check
   that it is still open — its backlog entry, plan status and the recent commits: a scenario already
   implemented has no current behavior left to characterize (trial finding F3). A full rewrite is
   a series of runs, one scenario each (strangler fig); parity grows run by run.

Gate: owner approval of the scenario and the permissions.

## Step 1 — Archaeology

Dispatch `references/archaeology-prompt.md` with `CHANGE_TARGET` = the chosen scenario.

## Step 2 — apply the map (coordinator)

With the step-0 permission, merge the report's *Draft AGENTS.md answers* into `AGENTS.md`
(preserve existing content and `<!-- BEGIN:... -->` blocks) and write `docs/surprises.md`
from its *Surprises* section. Only things an agent cannot derive from general knowledge.
Without permission, leave both as drafts in the report and say so in HANDOFF.md.

## Step 3 — access procedures (coordinator)

For each source the scenario needs (database, logs, CI results, deploy status) write a
reproducible read-only procedure: `docs/access/<source>.md` (what it is for, the command or
query, limits, what never to run) plus `scripts/access/<source>` when a command helps.
The owner creates the read-only credentials and puts them in the environment; never ask
for a secret in chat, never write one into a file or command line. A skill may wrap a
procedure but only points to these files. Gate: owner approval of the procedures.

## Step 4 onward

Product writes the scenario's **delta PRD** (`SPEC_PLAN/PRD.md`: scenario, goals, non-goals,
constraints — framing only) and creates `<SPECS_DIR>/INDEX.md` with the change's AC/QR as `planned`
(`references/specs-contract.md`); the owner approves both. Roles take framing from the delta
PRD and criteria only from INDEX. Then Consistency (`product`), Architect, Tech Lead,
Consistency (`full`) as in `references/pipeline-core.md`.
The plan's first slice is characterization; changing slices carry the `parity` gate
(`references/parity.md`).

## OBS decisions (after the characterization slice)

The characterization slice records current behavior of the scenario as `OBS-n` rows in
INDEX (Origin `OBS`) with labeled specs — a safety net, not a requirement. Present them to
the owner **in one batch for this scenario only**:

| OBS | Observed behavior | Recommendation | Decision |
|---|---|---|---|
| OBS-003 | wrong password → 401 forever, no lockout | BUG: lock after 5 tries | ← owner |

Each decision changes INDEX and the specs **in one commit**, so `index-check` stays green:

- **→ AC (intended):** applied right after the decision, inside the characterization slice:
  add `AC-m` restating the behavior (Origin `OBS`), relabel its spec `req:AC-m`, retire `OBS-n`.
  Behavior does not change; parity stays identical.
- **→ BUG (must change):** record the decision in `STATE_FILE` and the plan; INDEX keeps `OBS-n`
  active until the fix. The slice that implements the fix, in the same commit: adds `AC-m` with
  the desired behavior (Origin `deviation:OBS-n`), relabels the current spec to `req:AC-m` with
  the new expectation, retires `OBS-n`, and appends the parity delta (`references/parity.md`).
- **Undecided** OBS rows stay active and protective.
- A dangerous observation (security, money, data loss) is raised to the owner immediately,
  before any change, not batched.
