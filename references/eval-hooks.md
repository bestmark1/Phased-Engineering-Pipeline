# Eval hooks — when the product itself contains an LLM

Read this only when `{{EVAL_COMMAND}}` is set. Most projects have no LLM in the
product and need nothing here.

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

When `{{EVAL_COMMAND}}` is empty, skip this entirely — most projects have no LLM in
the product and need nothing here.

#### Cold start: a new project has no outputs to evaluate

Most eval tooling assumes production traces already exist. A project being built from
scratch has none — there is no code yet, so there is nothing to log. Do not let this
become a reason to defer evaluation until "later", which in practice means never.

Bootstrap in three steps, matched to what actually exists at each point:

**1. Spec-derived cases — available immediately, before any code.**
Every acceptance criterion about model behavior in the PRD is already an eval case.
"Given a Thai greeting, the translation preserves the politeness register" is a test
waiting for an input and an expected property. Write 10–20 such cases into
`SPEC_PLAN/EVAL_PLAN.md` during planning, each with a concrete input and what must be
true of the output. These are hand-written by the owner, not generated — a model
inventing its own success criteria grades its own homework.

**2. First real outputs — after the phase that produces them.**
The moment the LLM path runs end to end, capture its outputs. A few dozen real
responses are enough to see failure patterns the spec never anticipated. This is where
issue-discovery and judge-creation tooling becomes applicable; before this point it has
no input.

**3. Golden dataset and regression — once patterns are known.**
Promote reviewed cases into a golden set and wire `{{EVAL_COMMAND}}` into QA. From here
the normal loop applies: every escaped defect becomes a new case.

Until step 2, `{{EVAL_COMMAND}}` may legitimately run only the spec-derived cases, and
that is enough. An eval suite that covers ten hand-written cases well beats a perfect
methodology that starts after launch.

