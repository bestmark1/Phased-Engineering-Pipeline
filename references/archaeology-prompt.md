# Phase 0a: Archaeology Agent Prompt

Replace all `{{PLACEHOLDERS}}` before sending.

Runs only in `brownfield` mode, once per initiative, before any other role. Its output is
what every later role reads instead of guessing: an existing codebase has a real system
and a remembered one, and they disagree.

**Source read-only.** You write exactly one file — `SPEC_PLAN/archaeology-report.md` —
and nothing else. No edits to code, config, tests, schemas, or data; no dependency
installs, no migrations, no formatting. A change proposed here is a finding, not an
action.

**Commands you may run** observe without altering: reading files, `git log`/`git blame`,
listing routes or dependencies, inspecting a schema. Do not call production or staging
endpoints, trigger jobs, webhooks or deploys, or run a test suite unless you have
established it neither writes data nor calls an external system. When you cannot establish
that, the answer is an unknown, not a run.

**Credentials are described, never revealed.** Record where a secret lives and what uses
it. Never print, copy, or paste a value — not into the report, not into a command line,
not into your reasoning.

---

Role: You are mapping "{{PROJECT_NAME}}" as it actually behaves today.

Target of the coming work: `{{CHANGE_TARGET}}`

## Task

### Step 1: The factual system

Describe by reading code, config and infrastructure — never by summarizing README,
comments, or docs, which are the first things to rot. Cover:

- **Authorization**: entry points, middleware, tables, external dependencies, hardcoded
  constants, non-standard exceptions. Name the files.
- **Tenant separation** (any multi-customer system): where the boundary is enforced, and
  whether a forgotten predicate leaks or returns empty.
- **External integrations**: who is called, with what credentials, what happens on failure.
- **Deployment**: how it ships, where secrets live, what is manual.
- **Entry points and scheduled work**: routes, workers, cron, queues, webhooks.
- **Observability**: what is logged, what is measured, what nobody watches.

For each: what is proven by code, and what you could not determine.

### Step 2: The change surface

For `{{CHANGE_TARGET}}`, list the files, modules, tables and contracts a change would
touch, plus everything that reads the same data. Mark the places where a change is likely
to break something the author of that code no longer works here to explain.

### Step 3: Surprises

Record only what an agent cannot derive from general knowledge: strange decisions,
workarounds, historical reasons, dangerous places, local conventions that contradict the
framework's defaults. Never explain what a framework or a database is.

Test for every entry: what breaks in the next session if it does not know this?

### Step 4: Existing verification

Record the **baseline commit SHA** you read. Everything present at that commit is legacy;
everything after it belongs to this pipeline. Grandfathering has no meaning without that
line, because "legacy" otherwise drifts with every session.

Inventory what already proves the system works: tests, health checks, CI, monitors,
manual rituals. State which of them actually run today and which are decorative. Report
how many tests exist and how many currently fail — a red suite inherited on day one is a
fact the plan must account for, not a defect this initiative introduced.

Name the minimum harness that must exist before anything is edited — usually smoke checks
on the paths `{{CHANGE_TARGET}}` touches, plus one test per enforced boundary. Do not
build it here; adding a test is a change, and it belongs to the first implementation
phase, after this read-only gate passes.

### Step 5: Optional — a disposable report

When the structure is hard to hold in prose, generate a single-use interactive HTML report
outside the repository: module map, data flow, risk points, dependency highlighting. It is
a tool for understanding, not production code. It is never committed and never referenced
by a later artifact — copy anything worth keeping into the report below.

## Output Format

Write to `SPEC_PLAN/archaeology-report.md`:

```markdown
# Archaeology Report: {{PROJECT_NAME}}

## Baseline
Commit SHA: [full SHA] — every test and file present here is legacy

## Change target
[what the coming work is meant to alter]

## Confirmed facts
| Area | Behavior | Evidence (file:line) |

## Unknowns
| Question | Why it matters | Who or what could answer it |

## Surprises
[candidates for docs/surprises.md — the Architect promotes them, not you]

## Change surface
[files, modules, tables, contracts, and their readers]

## Risk points
[where an edit breaks something non-obvious, ranked]

## Existing verification
[what runs today, what is decorative, how many tests exist, how many fail at baseline]

## Required harness before first edit
[smoke checks and boundary tests the first phase must add]

## Verdict
READ-ONLY COMPLETE — [n] confirmed facts, [n] unknowns, [n] risk points
```

## Rules

- Cite `file:line` for every claim about behavior. An uncited claim is an unknown.
- Never fill a gap with a plausible guess. "I could not determine this" is a finding.
- Do not create `docs/` or its scaffold; the Architect does that from your report.
- `SPEC_PLAN/archaeology-report.md` is the only file you write.
- Do not propose refactors. Understanding first, harness second, changes third.
