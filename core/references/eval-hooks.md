# Eval hooks — when behavior in scope depends on an LLM

Read when LLM behavior is in scope, including when EVAL_COMMAND is still unset.
No LLM behavior: record n/a. LLM behavior without a runner: setup pending, not skipped.

If the product's behavior depends on a model — prompts, agents, RAG, classification,
generation — build/test/lint cannot express whether it works. Tests prove the code runs;
they say nothing about whether the output is any good.

For such projects:

- The Tech Lead defines `{{EVAL_COMMAND}}` and the phase that introduces it.
- Eval criteria are written **before** the implementation phase that needs them, and
  live in `SPEC_PLAN/EVAL_PLAN.md` alongside the acceptance criteria they extend.
- QA runs `{{EVAL_COMMAND}}` as part of Step 3 verification.

This pipeline does **not** implement eval metrics, judges, or datasets itself. Delegate
to dedicated eval skills (rubric design, judge/human alignment, golden datasets,
regression runs) and to established runners — promptfoo for CI-style assertions, Ragas
for retrieval metrics, Inspect AI for agent trajectories. PEP calls them; it does not
reimplement them.

An empty command does not establish non-applicability. Plan setup before the dependent
phase and return UNKNOWN if the required evaluation cannot run.

## Before an eval is trusted as a gate

An eval that cannot move is not evidence. Check the eval itself before the first gate
that depends on it, and again whenever the case set, grader, model or harness changes.
Record the results with the score; an eval whose health was never checked is UNKNOWN as
a gate, not PASS.

- **Headroom.** If the baseline already scores near the ceiling at the strongest
  configuration in scope, the eval can no longer show improvement; it still detects
  regressions, and keeps that job. Report it as saturated, move the objective to cost or
  latency at quality parity (`references/run-economics.md`), or add harder cases. A
  saturated eval is never a reason to stop running it.
- **Grader stability.** Grade the same outputs twice — at least ten, chosen to include
  passes, failures and borderline cases, since agreement on easy cases proves little. Any
  flipped verdict blocks use of the eval as a gate until the grader is fixed; record the
  sample size and the result. A programmatic grader is exempt only if it is deterministic
  by construction.
- **Plumbing separated from quality.** Timeouts, API errors, truncated responses and
  leftover state from an earlier run are infrastructure failures. Count them separately;
  never let them pass as model quality, in either direction.
- **Noise.** Measure run-to-run variation on an unchanged snapshot with at least three
  repeats, and record the observed spread with the number of repeats behind it. A single
  pair of runs is not a measurement. Noise belongs to the set and the metric that decides:
  measure it for each set a decision is read from, and for each decisive metric — score,
  cost, latency — since their variation differs. A set that is being kept unseen is
  measured when it is finally run, not before (`references/hillclimbing.md`). If the noise
  is larger than the smallest difference that would change a decision, the eval cannot
  support that decision: add cases or repeats instead of reading the number.
- **Expected ordering.** A stronger model or higher effort should not score worse. When
  it does, suspect ambiguous cases or a miscalibrated grader before crediting the result.

## Choosing the grader

Take the cheapest grader the output allows:

1. **Programmatic check** — exact match, a label from a fixed set, JSON against a schema,
   a passing test. Preferred whenever the output space is constrained.
2. **Model judge** — only for open-ended output with many valid answers and stated quality
   criteria. The judge is not the model under test. Its rubric is a list of checkable
   claims, not a 1-to-5 scale. When a baseline exists, give the judge both outputs in
   random order without saying which is which, and have it pick the better one.

Before either grader is trusted, the owner or a domain expert reads a sample of already
graded cases and says where they would have graded differently. A grader nobody audited
produces confident numbers of unknown meaning, and a miscalibrated grader is one of the
most common reasons an eval misleads.

## Choosing cases

- State why a case is hard before including it. A case whose difficulty nobody can
  explain is usually ambiguous, and an ambiguous case fails regardless of the change.
- A case that fails every run in every configuration is a suspected broken case or
  grader. Diagnose it before treating it as a product defect.
- Do not assemble the set from what today's model happens to get wrong: that measures one
  model's weak spots, not what the product must do. Difficulty is judged by a person.
- Sources, in order: real production or user-reported failures; bug reports and tickets;
  five to ten cases written by hand; synthetic cases anchored in real ones. User traffic
  alone skews easy, because people try what they expect to work.
- Every case a grader checks must be answerable from the case itself: two domain experts
  reading it should reach the same verdict.

#### Cold start: a new project has no outputs to evaluate

Most eval tooling assumes production traces already exist. A project being built from
scratch has none — there is no code yet, so there is nothing to log. Do not let this
become a reason to defer evaluation until "later", which in practice means never.

Bootstrap in three steps, matched to what actually exists at each point:

**1. Spec-derived cases — available immediately, before any code.**
Every acceptance criterion about model behavior in the PRD is already an eval case.
"Given a Thai greeting, the translation preserves the politeness register" is a test
waiting for an input and an expected property. Draft a representative starter set in
`SPEC_PLAN/EVAL_PLAN.md` during planning, each with a concrete input and what must be
true of the output. An agent may draft cases; the owner/domain expert reviews and
approves expected properties before acceptance use. Do not equate model-generated
expectations or self-grading with independent validation. Cover meaningful failure
paths as well as happy paths; the number is driven by risk, not a fixed quota.

**2. First real outputs — after the phase that produces them.**
The moment the LLM path runs end to end, capture its outputs. A few dozen real
responses are enough to see failure patterns the spec never anticipated. This is where
issue-discovery and judge-creation tooling becomes applicable; before this point it has
no input.

**3. Golden dataset and regression — once patterns are known.**
Promote reviewed cases into a golden set and wire `{{EVAL_COMMAND}}` into QA. From here
the normal loop applies: every escaped defect becomes a new case.

Until step 2, `{{EVAL_COMMAND}}` may legitimately run only the spec-derived cases, and
that is enough. A reviewed, bounded starter suite beats a perfect
methodology that starts after launch.

