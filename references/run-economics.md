# Run economics and pipeline-development caching

Every gate and phase costs real money and time. Record it; do not gate on it yet.

Track per phase in `PROGRESS.md`: tokens in/out, wall-clock duration, approximate cost,
and how many review round-trips the phase needed.

Thresholds stay **report-only** until enough comparable runs exist to know the normal
spread. A cost or latency budget invented before that data is either meaningless or a
source of false failures. Revisit once a baseline exists.

### Cached model calls when iterating on the pipeline itself

When debugging or tuning the pipeline (editing role prompts, reordering gates, changing
models), enable response caching for model calls so repeated runs over unchanged inputs
are free. Paying full price to re-observe an unchanged step is the largest avoidable
cost in pipeline development.

Caching applies to **pipeline development only**. Real project runs must execute
uncached — a cached verdict on changed code is not a verdict.

