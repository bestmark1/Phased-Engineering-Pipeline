# Parity — the frozen suite decides whether behavior changed

Loaded by Tech Lead (to plan the gate), Developer and QA in any slice that touches the run's
scenario. Script: `scripts/parity.py`.

## Baseline (characterization slice)

1. The characterization specs are committed; that commit is `suite_sha`. Freeze with it the
   paths the specs need: `specs/` (including `specs/support/`) and, if outside it, fixtures,
   seed and test config (`--suite-path` per path).
2. Record the environment fingerprint as JSON (`env.json`): seed/fixture identity, test config
   hash, runtime and service versions. Same file for every later run.
3. Run against the original system:

   ```bash
   python3 <skill-root>/scripts/parity.py run --suite-sha <suite_sha> --product-sha <baseline_sha> \
     --command "<project spec command>" --env-file env.json --out SPEC_PLAN/parity/<scenario>/baseline.json
   ```

   The spec command writes `{spec_id: {"outcome": "pass"|"fail", "observation": "<observed
   response/output>"}}` to `$PARITY_RESULTS`. Observations are concrete (status + body, rendered
   text, exit code + output), so a changed message is a changed behavior.

## Every changing slice (`parity` command gate)

```bash
python3 <skill-root>/scripts/parity.py run --suite-sha <suite_sha> --product-sha <snapshot> \
  --command "<same command>" --env-file env.json --out SPEC_PLAN/parity/<scenario>/<snapshot>.json
python3 <skill-root>/scripts/parity.py compare SPEC_PLAN/parity/<scenario>/baseline.json \
  SPEC_PLAN/parity/<scenario>/<snapshot>.json --deltas SPEC_PLAN/parity/<scenario>/deltas.json \
  --index specs/INDEX.md
```

- Always the frozen `suite_sha`, never the current specs: specs edited together with the code
  would pass by construction. Editing current specs is allowed; it never replaces this run.
- **Approved delta** = one entry in `deltas.json` per changed spec: `{spec, expected_old,
  expected_new, obs, ac}` with the exact old and new result, and `ac` an active INDEX row with
  Origin `deviation:<obs>` (an owner BUG decision, `references/entry-prompt.md`).
- **Verdict:** PASS = every spec identical or matching its delta (the frozen spec may then
  exit nonzero — expected). FAIL = a change without a matching approved delta, a different
  suite, or specs outside the baseline. UNKNOWN = a spec not run or a different environment.
  FAIL and UNKNOWN both block Done (exit 1); the receipt records the `parity` command with that
  exit code. A spec failure inside the run is data; only the comparison is the verdict.
