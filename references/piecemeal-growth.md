# Mode: Piecemeal Growth

A loadable review mode, not a standing instruction. Load it **after** a change is green,
point it at a specific diff, and ask what can be removed. Keeping this text permanently in
context biases the Developer toward under-implementing new work — the standing rule lives
in Core principle 8 instead, and it is deliberately weaker than what follows.

## The stance

Piecemeal growth designs from forces that exist now: executable requirements, current
workflows, and failures that have actually occurred. Like a desire path, the shape follows
observed traffic; it is not paved in anticipation of journeys nobody has taken.

Keep the implementation as narrow as the present contract. Configurability, concurrency,
fallback paths, validation, and abstractions for possible future uses are all cost paid
today against a benefit nobody has yet demanded. Make assumptions explicit and let
violations fail loudly, so new pressure becomes visible instead of being absorbed by
speculative machinery.

When a new requirement or a repeated failure appears, repair the design locally.
Generalize only once reality has shown what the generalization must support.

## The boundary that survives

This is not an argument against integrity at real boundaries. Durable data, external
callers and inputs, security boundaries, and failures with demonstrated likelihood or cost
keep proportionate rigor before the first incident. It is an argument against paying
complexity for imagined risks, not against paying it for established ones.

## How to run it

Given a diff, a plan, or an architecture draft, classify every element you would question:

| Verdict | Meaning | Required evidence |
|---|---|---|
| **KEEP** | A present force demands it | the clause, workflow, or observed failure it answers |
| **REMOVE** | Serves only a hypothetical future | what would have to become true before it earns its place |
| **QUESTION** | Cannot tell from the artifact alone | the fact needed to decide, and who holds it |

Rules for the run:

- Report findings; do not delete anything yourself. A removal is an ordinary change and
  goes through the same phase scope, deterministic checks, and review as any other.
- Every REMOVE names the speculative future it serves. "Simpler" is not evidence.
- Anything inside the boundary above defaults to KEEP unless the artifact shows the risk
  is neither durable, external, security-relevant, nor demonstrated.
- Say so plainly when nothing should be removed. An empty finding list is a legitimate
  result and a cheaper one than an invented cleanup.

## When to load it

- After a phase goes green, before the LLM reviewers — see *Subtraction pass* in `SKILL.md`.
- On explicit request to shrink an existing solution.

Do not load it while writing new code for an unfinished phase.
