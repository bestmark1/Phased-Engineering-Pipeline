# Run economics and pipeline-development caching

Record measured tokens, wall-clock duration, review round-trips and cost per phase in
PROGRESS.md when available. Missing counters/prices stay `unavailable`, never invented
zeroes. Label cost estimates with their basis; do not pretend estimates are invoices.

Newly inferred thresholds are report-only until calibrated on comparable runs. This does
not override an explicit token/cost/time budget: pause before exceeding an agreed limit
and ask for a decision. Do not make paid extra calls merely to collect these statistics.

## Caching while developing the pipeline

Cached responses may test wiring/format against unchanged inputs; label them cached.
Reuse requires identical artifact snapshot, prompts/rubric, tool context, model/settings
and configuration. A changed input invalidates the verdict. Cache hits are not fresh
independent acceptance. Real acceptance and stability/nondeterminism evaluations use
fresh runs; never use cached outputs to claim repeatability of a stochastic model.
