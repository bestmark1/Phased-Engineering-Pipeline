# Trial run: existing-system-pipeline on Trend watching — 2026-10-06

Scenario TW-X-TIMELY-NEWS (publish important fresh news to X right after fact check). Offline
steps 0–5, separate worktree at `582eb20`, branch `trial/timely-news-existing-system`.
Owner decisions: first scenario (X Premium) dropped as already applied; Architect and
Consistency(full) replaced by a seam audit by reading (cost); new-product trial deferred to a
real project.

## What worked
- Skill selected itself correctly (no executable specs, no specs job).
- Archaeology: READ-ONLY COMPLETE, 35 facts / 14 surprises / 10 risks; 2 claims spot-checked true.
- ID rules held through 3 Product revisions: changed meaning → retire + new ID, never renumber.
- Gate loop converged: Consistency(product) FAIL (8 major, e.g. t.co link breaks read-back
  equality; speed criterion unverifiable in observe-only) → targeted repair → re-check PASS.
- Reviewer separated document PASS from owner approval (asked for re-approval of material changes).

## Findings from running (F1–F7)
- F1 `specs/` already used by the project for Markdown specs → configurable specs root needed.
- F2 shared PROGRESS/HANDOFF owned by other sessions → initiative-scoped state file needed.
- F3 entry step must verify the scenario is still open before owner approval.
- F4 `validate_gate.py --prompt` blocks the role prompts' own preamble line; 3+ wordings in 17 places.
- F5 product-prompt unaware of "delta PRD = framing, criteria in INDEX".
- F6 consistency-prompt refers to new-product PROGRESS rows (`0c`).
- F7 tech-lead-prompt unaware of characterization slice / OBS / parity gate.
- F8 (design defect) index-check required on every receipt + "every active spec row needs a spec" made
  a characterization slice impossible to pass (delta ACs get specs later). Fixed: status `planned`.
- F9 suite_sha needs committed specs + INDEX; the skill did not say who commits initiative artifacts under
  which permission. Addressed by gate-policy's commit rules + owner permission recorded at step 0.
- F10 parity output path hard-coded to SPEC_PLAN/parity/. Fixed: `<INITIATIVE_DIR>`.
- F11 failing frozen spec recorded pytest's message instead of the observed value. Fixed in parity.md; the
  script rejects duplicate spec ids.
- F12 "no network / paid calls" was declared, not enforced. Fixed: scripts/hermetic_guard.py + required guard.
- F13 a reviewer ran env-sensitivity probes without a guard (likely 2 real `codex exec` calls, synthetic
  text). Fixed: reviewer prompts forbid unguarded experiments.
- F14 characterization specs pinned the value they characterized (timezone, then freshness window).
  Fixed: contract rule + mutation check in review.

## Seam audit by reading (G1–G19)
Only archaeology is fully pipeline-aware; 10 of 11 role prompts need pointers or edits.
Verified by coordinator: G1, G2.

| ID | Prompt | Pipeline | Problem | Fix |
|---|---|---|---|---|
| G1 | tech-lead 113-148,197 | ES | "every phase ends with something a user can do" contradicts characterization slice 1; "every PRD story" vs INDEX | ES branch: slice 1 = characterization, exempt; cover active INDEX rows |
| G2 | developer 47-50 | NP+ES | allows requirement ID "in a one-line comment"; check_index ignores comments | specs/: `req:<ID>` string literal only; point to specs-contract |
| G3 | tech-lead 64-79,189-197 | NP+ES | plan gate set misses specs job, dependency linter, index-check/index_present, initiative receipt gates, NP INDEX transfer before final QA | "Required gate set" paragraph |
| G4 | developer 28-81,162-175 | ES | no parity procedure, same-commit OBS→AC rule, "characterization must not change behavior" | ES pointer to parity.md + entry OBS section; parity in checklist/report |
| G5 | qa 19-22,109-122,216-222 | ES | OBS rows not excluded from QA lists/coverage/blind inputs | exclude OBS; guarded by specs job + parity |
| G6 | developer, architect | NP+ES | black-box specs rules absent | 3 lines + pointer |
| G7 | qa 154-163 | NP+ES | Step 3 misses specs job, index-check, parity, quality ratchet | add plan command gates |
| G8 | product 125-211 | NP+ES | INDEX format/Origin, append-only on existing INDEX, NP post-release BACKLOG flow | "Requirement source" block |
| G9 | reviewer-solid 47-56 | NP+ES | specs label/assertion rules not named | 2 lines |
| G10 | reviewer-solid/sre, pipeline-core | NP+ES | "combined SOLID/SRE review" has no prompt; envelope id/rubric not stated; depth not an input | REVIEW_DEPTH input, ids per plan, combined mode |
| G11 | consistency 37-74 | ES | "stories without AC" false Critical on delta PRD; no INDEX/gate-set/characterization checks; progress-template rows vs ES flow | pipeline note + checks |
| G12 | archaeology 16-20 vs 67-81 | ES | exact failing-test baseline demanded but suite may not be run; no INDEX/specs-job/parity-input inventory | "baseline pending: coordinator runs isolated"; 3 items |
| G13 | architect 101-142,161-182 | NP | never loads quality-profile/observability ADR; test policy lacks req: labels; no specs layer | pointers |
| G14 | tech-lead 64-79 | NP | quality gate table by depth not referenced | pointer |
| G15 | developer 80,134 | NP | ratchet baseline must not be regenerated | 1 line |
| G16 | qa 174-196 | ES | scope creep / orphan tests measured against PRD, not requirement source | "requirement source" |
| G17 | several | NP+ES | mode names and PROGRESS row numbers mixed | mode legend + ES row map |
| G18 | analyst 58-71 | ES | writes docs/ without step-0 permission; no archaeology input | permission + SPEC_PLAN/research.md |
| G19 | retro 14-30,87-91 | ES | ignores past-session transcripts; may edit specs/ or parity | include transcripts; prohibit |

A generic coordinator-pasted "pipeline context" block covers ~8 rows; G1–G4, G6–G7, G10,
G12–G15 need role-specific edits (G1, G2 are explicit contradictions a block cannot override).
