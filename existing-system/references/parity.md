# Parity — the frozen suite decides whether behavior changed

Loaded by Tech Lead (to plan the gate), Developer and QA in any slice that touches the run's
scenario. Script: `scripts/parity.py`.

## Baseline (characterization slice)

`<INITIATIVE_DIR>` is the project setting (`references/pipeline-core.md`; default `SPEC_PLAN`).
The spec command runs under the hermetic guard and a clean environment (`references/specs-contract.md`).

0. The runner creates `<INITIATIVE_DIR>/parity/<scenario>/` on first use. Commit an empty delta list
   `<INITIATIVE_DIR>/parity/<scenario>/deltas.json` = `[]` with the baseline.
1. The characterization specs are committed; that commit is `suite_sha`. Freeze with it the
   paths the specs need: `specs/` (including `specs/support/`) and, if outside it, fixtures,
   seed and test config (`--suite-path` per path).
2. Record the environment fingerprint as JSON (`env.json`): seed/fixture identity, test config
   hash, runtime and service versions. Same file for every later run.
3. Run against the original system:

   ```bash
   python3 <skill-root>/scripts/parity.py run --suite-sha <suite_sha> --product-sha <baseline_sha> \
     --suite-path <SPECS_DIR> [--suite-path <fixtures/config>...] --command "<project spec command>" --env-file env.json --out <INITIATIVE_DIR>/parity/<scenario>/baseline.json
   ```

   The spec command writes `{spec_id: {"outcome": "pass"|"fail", "observation": "<observed
   response/output>"}}` to `$PARITY_RESULTS`. Record the **observed value on pass and on
   fail** — never the assertion message, which is tool-version text an approved delta could not
   match; if the product errors before the value exists, record `ERROR: <type>`. Two specs writing
   the same id is an error, not an overwrite (trial finding F11). Observations are concrete (status + body, rendered
   text, exit code + output), so a changed message is a changed behavior.

## Every changing slice (`parity` command gate)

```bash
python3 <skill-root>/scripts/parity.py run --suite-sha <suite_sha> --product-sha <snapshot> \
  --suite-path <SPECS_DIR> [--suite-path <fixtures/config>...] --command "<same command>" --env-file env.json --out <INITIATIVE_DIR>/parity/<scenario>/<snapshot>.json
python3 <skill-root>/scripts/parity.py compare <INITIATIVE_DIR>/parity/<scenario>/baseline.json \
  <INITIATIVE_DIR>/parity/<scenario>/<snapshot>.json --deltas <INITIATIVE_DIR>/parity/<scenario>/deltas.json \
  --index <SPECS_DIR>/INDEX.md
```

- Always the frozen `suite_sha`, never the current specs: specs edited together with the code
  would pass by construction. Editing current specs is allowed; it never replaces this run.
- **Approved delta** = exactly one entry in `deltas.json` per changed spec: `{spec, expected_old,
  expected_new, obs, ac}` with the exact old and new result, and `ac` an active INDEX row with
  Origin `deviation:<obs>` (an owner BUG decision, `references/entry-prompt.md`). `--index` is
  mandatory: without INDEX confirmation a changed spec is FAIL. Duplicate or malformed deltas
  are input errors (exit 2).
- **Suite paths** are repository-relative (`specs`, `fixtures/…`, `config/test…`); absolute paths,
  `..` and `.git` are rejected before anything is touched. Freeze every fixture and config the
  specs read, or a change to them hides a behavior change.
- **Verdict:** PASS = every spec identical or matching its delta (the frozen spec may then
  exit nonzero — expected). FAIL = a change without a matching approved delta, a different
  suite, or specs outside the baseline. UNKNOWN = a spec not run or a different environment.
  FAIL and UNKNOWN both block Done (exit 1); the receipt records the `parity` command with that
  exit code. A spec failure inside the run is data; only the comparison is the verdict.
