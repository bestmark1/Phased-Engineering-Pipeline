# Hillclimbing — a phase that tunes model behavior against an eval

Load this only for a slice whose deliverable is better model behavior or lower cost at
parity, achieved by changing prompts, skills/instruction files, tool descriptions, model
or effort settings, or narrowly scoped harness code. A slice that implements a feature
uses the normal Developer flow instead. Unload afterwards.

This pipeline does not implement the search. Use existing tuning tooling where the project
has it; these rules govern what counts as evidence either way.

## Preconditions

- An eval exists and passed the health checks in `references/eval-hooks.md`. Noise is
  measured per decisive metric on the tuning and guard sets only — the final set stays
  unrun, and its noise is measured from the repeats of its single evaluation at the end.
  Without those numbers no round can be judged.
- Noise is smaller than the smallest improvement that would change a decision. If it is
  not, add cases or repeats first; rounds below the noise floor cannot be measured.
- The objective is stated before the first round, with the metric that decides a round:
  quality, or cost/latency at quality parity. For a cost objective, also state the parity
  band — how much quality may move and still count as unchanged; absent a reason, that
  band is the eval's noise. A saturated eval supports only the cost objective.
- The surface that may change is named, cheap to revert, and plausibly responsible for the
  metric. Open-ended harness rewrites are out of scope for this mode.
- Cases are split at random into three parts, recorded with the plan:
  - **tuning set** — the only set whose failures may be read;
  - **guard set** — run each round to detect overfitting, never read for failure content;
  - **final set** — untouched until completion and evaluated once, for the reported result.

  Each guard-set run spends some of its independence: a set consulted every round for many
  rounds eventually steers the search. Budget the number of rounds before starting; when
  the budget runs out, stop, or re-split with new cases before claiming a result. The final
  set is never used to keep, revert or choose anything.

## One round

1. Read failures from the **tuning set only**.
2. Propose exactly one change, as a patch, aimed at the root cause — the rule or section
   that produces the failure, not a reworded line.
3. Run the eval on the tuning and guard sets. Never on the final set.
4. Decide by the objective's metric, and record both scores, cost and the noise:
   - **quality objective:** keep when quality improves beyond noise on the tuning set and
     the guard set does not regress beyond noise. Tuning up while the guard set is flat
     across repeated rounds is the overfitting signal — revert and change approach.
   - **cost objective:** keep when cost falls by at least the stated margin — which must
     exceed the measured run-to-run variation of cost itself, not of the quality score —
     and quality stays inside the parity band on both sets. Savings never justify a quality
     regression beyond that band, and a quality gain does not excuse a cost increase.
   - any regression beyond that metric's own measured noise → revert;
   - movement within that metric's own measured noise → no evidence, revert.

## Leak rules

Overfitting is not only a score artifact; it is usually leaked case content.

- Never paste case content — inputs, expected outputs, transcripts, judge verdicts — into
  a prompt, skill, tool description or harness.
- A fix must be a general rule, statable without naming the case that motivated it. A rule
  that only helps one case is a leak with extra steps.
- Keep expected answers structurally out of the model's reach at runtime: the eval's
  answers must not live where the product or agent can read them mid-task.
- Environment state from an earlier trial (files, git history, caches) must not survive
  into the next one; it hands over answers and inflates the score.

## Stalling

After two or three rounds without a measurable gain — or immediately when no single
available fix could exceed the noise — stop editing and triage every remaining tuning
failure by cause: ambiguous case, broken grader, plumbing error, genuine behavior gap.
Fix eval defects as eval defects; changing an approved artifact follows
`references/artifact-changes.md`. Continue rounds only on genuine gaps, or stop and report
that the eval, not the product, is now the limit.

## Completion

- Choose the candidate configuration from the tuning and guard runs, then evaluate it and
  the baseline on the **final set** in one comparison, with repeats, so that set's own
  noise is measured in the same pass. That single comparison is the reported result.
- Report it with its noise, the number of rounds and guard-set runs spent, the rounds kept
  and reverted, and the cost delta when cost was in scope (`references/run-economics.md`).
- A gain within noise is reported as no measurable improvement. It is not a completed
  objective, and it is not evidence for an acceptance criterion.
- Changed prompts, models or effort settings invalidate dependent evidence: rerun the
  affected checks, reviews and criteria per `references/gate-policy.md` before Done.
- A model, provider or effort change with cost, privacy or dependency consequences is an
  owner decision, not a tuning detail.
