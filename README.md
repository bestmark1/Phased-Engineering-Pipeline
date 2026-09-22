# phased-engineering-pipeline

A phased workflow for substantial end-to-end initiatives: product framing, architecture,
vertical slices, independent review and reproducible QA. Not a default process for small fixes.

## Current workflow

[SKILL.md](SKILL.md) is the entry point. It preserves Product, optional Domain Analyst,
Archaeology, Consistency, Architect, Tech Lead, Developer, SOLID/SRE reviewers, QA and Retro.
The pipeline does not select models; existing agent/model settings remain separate.

- **Full:** new framing with Narrative + MRD + PRD, followed by architecture and delivery.
- **Lite:** reuse approved framing/architecture, record applicability and implement a delta.
- **Brownfield:** read-only archaeology and an exact test baseline, then Lite delivery.
- Coordinator initializes PROGRESS before Product/research. Roles report readiness, not
  acceptance; Done requires the approved checks, independent review and owner approvals.
- Reviewer depth follows impact and the project floor. Critical configuration/dependency
  changes remain High. Final QA uses an isolated checkout of an exact commit.
- Runtime ACs need runtime observations. Internal QRs use their approved static/contract
  or runtime check. Data recovery needs a disposable restore test, not just a code revert.
- No automatic commit/push/PR/deploy. An explicit owner request authorizes an action;
  writing it into a Definition of Done does not. Preserve unrelated uncommitted changes.

The canonical contracts are [gate-policy.md](references/gate-policy.md),
[role-inputs.md](references/role-inputs.md), and
[artifact-changes.md](references/artifact-changes.md). They define STRICT_MODE,
exact baseline exceptions, shared JSON verdicts, resolved inputs and stable AC/QR IDs.
STRICT_MODE=false makes noncritical major findings advisory, not safety or checks optional.

## Installation / updating

Review the source and local modifications before installing. Do not extract over an
existing modified installation; compare and back up first. The .skill bundle is gzipped
tar despite its extension. For a **new empty destination**, extract with:

```bash
mkdir -p /path/to/empty-skill-directory
tar -xzf phased-engineering-pipeline.skill -C /path/to/empty-skill-directory
```

The package root contains SKILL.md, references/, scripts/ and tests/. Install the complete
package into the skill root appropriate for the host. No Python packages are required.

## Usage

Request a phased pipeline for a substantial initiative, e.g. “Plan and build this
end-to-end feature with the phased-engineering-pipeline”. Ordinary bugfixes and small edits
should not require this workflow. Existing approved decisions should not be re-interviewed.
Configuration is resolved from project artifacts and tooling; see SKILL.md for the table.

## Local validation

```bash
python3 scripts/validate_gate.py /path/to/project/SPEC_PLAN/gates/3.1.json
python3 scripts/validate_gate.py --prompt /path/to/rendered-brief.txt
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The validator checks supplied evidence records and unresolved tokens. It neither executes
project checks, installs a hook, changes progress nor verifies that an approval is genuine.
The coordinator still compares gate coverage to the approved plan and inspects actual outputs.
An accepted legacy exception is reported explicitly, never rewritten as a green test exit.

## Supporting references

- [progress-template.md](references/progress-template.md): state and receipt links.
- [docs-scaffold.md](references/docs-scaffold.md): project knowledge base, created as needed.
- [eval-hooks.md](references/eval-hooks.md): LLM behavior requires planned evals; an unset
  command means pending setup, not no LLM. Agents may draft cases; domain owners approve expectations.
- [run-economics.md](references/run-economics.md): observed telemetry, explicit budgets,
  and cache boundaries. Unavailable values are not invented.
- [piecemeal-growth.md](references/piecemeal-growth.md): grounded advisory subtraction.

On failure, repair the specific cause and recheck affected behavior. Repeated failure
requires diagnosis, not another blind retry. Material changes to approved behavior,
contracts, costs or permissions return to owner approval. QA never ships automatically.

## Verification scope

The bundled tests exercise the receipt validator, not autonomous model behavior or every
application stack. A full live multi-role run is a separate integration test. Git is
needed for snapshot/checkout operations; a provider CLI is only needed for an explicitly
authorized provider action. No model mapping is configured by this package.

## Historical release notes (not the current execution contract)

The following is retained from the previous README as historical context. Its process,
thresholds, quantitative estimates and claims are not current instructions or newly
verified results; where they differ, use SKILL.md and gate-policy.md above.

> ## New in v2 — Harness Engineering Upgrade
>
> Inspired by OpenAI's [Harness Engineering](https://openai.com/index/harness-engineering/) practices:
>
> | Feature | Description |
> |---------|-------------|
> | `docs/` knowledge base | Scaffold created by Architect, populated throughout pipeline |
> | `AGENTS.md` | Project map (≤60 lines): five questions, pointers instead of prose |
> | Decision Log | Each plan phase documents choices made and why |
> | Tech Debt Tracker | `docs/tech-debt-tracker.md` — tracked debt is acceptable, hidden is not |
> | Self-Review Loop | Developer: verify → self-fix → re-verify before handing off |
> | `STRICT_MODE` | `false` = advisory reviews for prototyping, `true` = all gates blocking |
> | llms.txt caching | Analyst saves distilled docs once; subsequent agents reuse |
> | Quality Score | QA updates `docs/QUALITY_SCORE.md` with coverage grades per layer |
> | Layer violations | SOLID reviewer checks dependency flow direction |
> | Boring tech principle | Architect avoids "magic" libraries; prefers stable, documented deps |
>
> ---
>
> ## New in v3 — Gate Discipline
>
> The pipeline's reviewers are themselves LLMs. v3 treats them as such: as fallible judges
> that cost money, drift, and share blind spots with the model that wrote the code.
>
> | Feature | Description |
> |---------|-------------|
> | Evidence hierarchy | Environment checks > tests > contracts > human review > LLM judge. A judge never overrides a stronger source |
> | Deterministic-first gates | build / lint / typecheck / test run before any reviewer is invoked — a linter proves for free what an LLM guesses at |
> | Review depth by risk | `low` / `medium` / `high` per phase. A config bump does not cost what a payment flow costs |
> | Structured verdicts | `criterion` / `status` / `severity` / `evidence` / `fix` / `rubric_version` instead of prose a developer cannot act on |
> | `UNKNOWN` verdict | A criterion with no checkable evidence is not a failure. Forcing binary answers manufactures both false approvals and false blocks |
> | Critic loop | Fix only the findings, re-review only the failing criteria, escalate after three rounds on one criterion |
> | Escalation over repetition | Re-running one reviewer measures judge stability, not code quality. Escalate on uncertainty instead |
> | Agent guardrails | Refuse out-of-scope deletion, secret leakage into commits or logs, history rewrites, and unrequested outward-facing actions |
> | Run economics | Tokens, duration, cost and review round-trips recorded per phase — report-only until a baseline exists |
> | SKILL.md stays lean | Entry point holds the flow, gates and principles; role detail loads from `references/` only when that role runs |
> | Quality command gate | Optional `{{QUALITY_COMMAND}}` settles measurable properties (complexity, cycles, dead code, duplication, secrets) with the project's own thresholds, failing only on new or worsened violations; reviewers cite it instead of judging numeric limits by taste, and still report concrete defects the tool missed |
> | Test strength | Reviewers ask whether each test would fail if its behavior broke; a weak test as the only evidence for a criterion is a major finding, and QA reports that criterion UNKNOWN unless stronger runtime evidence exists |
> | Discovery and reuse | A raw brief gets a one-question-at-a-time interview before the PRD; the analyst compares open-source candidates with licenses, and the architect records adopt / fork / build |
> | Eval hooks | Optional `{{EVAL_COMMAND}}` and `SPEC_PLAN/EVAL_PLAN.md` for products containing an LLM. The pipeline calls eval tooling; it does not reimplement metrics or judges |
>
> ### Context practices — what the project leaves behind for the next session
>
> | Feature | Description |
> |---------|-------------|
> | `docs/surprises.md` | Only what an agent cannot derive from general knowledge: workarounds, hidden constraints, dangerous places. Never "what a database is" |
> | Short `AGENTS.md` | Capped at 60 lines, five questions, pointers instead of prose. Detail lives in the docs tree |
> | Tests are evidence | A test proves a named requirement — an acceptance criterion, an architecture constraint, or a defect that must not return. Traceability, not scarcity: orphan tests are the defect, thorough coverage is not |
> | Black-box acceptance criteria | Criteria describe what the user observes, never internals — the implementation stays replaceable |
> | Session-archaeology retro | After QA PASS: where the agent stalled, what context was missing, then minimal fixes to `AGENTS.md` and `docs/` |
>
> ---
>
> ## New in v3.1 — Does it actually work
>
> Documentation and review were the strong parts; proving the product runs was not. v3.1 closes that gap.
>
> | Feature | Description |
> |---------|-------------|
> | QA exercises the running product | Criteria are verified by starting the product and observing it, not by tracing functions. Evidence is `POST /api/session → 201`, not a file path. No runnable environment means `UNKNOWN`, never `PASS` |
> | Release verification | QA's clean checkout installs and starts, `.env.example` complete, migrations reversible, health check answers — and every criterion is then exercised inside that checkout. Catches the build that works only in the agent's session |
> | Vertical slices | Phases are user-visible slices, not layers. A walking skeleton first, one scenario per phase after. Nothing waits until the last phase to work |
> | Scope by intent | The plan's file list is an expectation, not a whitelist — lockfiles and generated files need no amendment; an unplanned capability does |
> | Artifact change protocol | When implementation proves an approved artifact wrong: update the earliest artifact invalidated, propagate downstream, stop for approval when the change is material |
> | Quality requirements | Security, privacy, performance, accessibility and data recovery get stated in the PRD with a verification method — instead of being discovered at release |
> | Real exit codes | "Build would pass" is no longer an acceptable result. Commands are run and their exit codes reported, or named as not run with a reason |
> | Git hygiene | Clean tree before a phase; stage files by name. `git add .` is how `.env` files and credentials reach commits |
>
> ---
>
> ## New in v3.3 — Existing code, stable IDs, and a pass that removes
>
> Three additions, each answering something the pipeline could not do before.
>
> | Change | Rationale |
> |---------|-------------|
> | `brownfield` mode + read-only Archaeology role | The flow began at Product, so entering a codebase it did not write had no path: the first act would have been editing a system nobody had mapped. Archaeology describes what the code actually does, citing `file:line`, and writes one file — its own report — while leaving source, config, tests and data untouched. Legacy tests are grandfathered so the first QA run reports real findings instead of hundreds of orphans |
> | Subtraction pass + `piecemeal-growth.md` mode | Every gate asked whether something was missing; none asked what could be removed. Agents add configuration, fallbacks and abstractions for futures nobody ordered. The mode is loaded on demand and reports KEEP/REMOVE/QUESTION with evidence — held in standing context it would bias the Developer against finishing new work, so principle 8 carries a deliberately weaker standing form |
> | Stable criterion IDs (`AC-001`, `QR-001`) | QA used to number criteria at validation time, after the PRD, the traceability matrix and the tests had each referred to them differently. IDs are now assigned once where criteria are written and reused verbatim downstream. Flat, not hierarchical: `2.4.1` is an address and a position at once, so restructuring forces a choice between breaking references and keeping a misleading number |
>
> ---
>
> ## New in v3.2 — Fewer roles, leaner entry point
>
> A role earns a separate invocation only where it must **not** be the author of what it
> judges. Roles that all author were merged; independence was preserved everywhere it does
> real work.
>
> | Change | Rationale |
> |---------|-------------|
> | Product = Narrative + MRD + PRD | All three author, none judge. One pass writes the requirements with the framing still in context, and one owner approval covers all three artifacts |
> | Consistency = Clarifier + Analyzer | Same job — contradictions, gaps, ambiguity — at two moments. One prompt, invoked with scope `product` after approval and `full` after the plan. Both gates unchanged |
> | QA & Release in one clean checkout | Both need the product running. Verifying criteria in the directory that built them proves it works *there*; a fresh clone proves it works anywhere. One setup, two proofs |
> | Architect and Tech Lead kept separate | Merging would save one context load but remove the gate where the owner can redirect the design before planning effort is spent |
> | Plane MCP removed | An unused optional integration still cost a role, a prompt, an artifact, four placeholders and two rules — read on every activation. Execution state lives in `PROGRESS.md` |
> | `SKILL.md` 836 → 504 lines | Detail moved into `references/`, loaded when its role runs. Nothing deleted |
>
> **On repeated runs.** Requiring the same reviewer to pass an artifact k times in a row is
> not a reliability gain — repeated calls to one model with one prompt are correlated, and
> unanimity rejects correct work at compounding rates (a judge that approves good work 90%
> of the time passes it only 73% of the time across three runs). v3 escalates on genuine
> uncertainty instead, at roughly 1.1–1.3× cost rather than 3×.
>
> ---
>
