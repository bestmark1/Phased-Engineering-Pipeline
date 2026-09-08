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

