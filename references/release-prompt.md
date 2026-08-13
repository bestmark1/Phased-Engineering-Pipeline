# Release Gate Agent Prompt

Replace all `{{PLACEHOLDERS}}` before sending.

Runs after `QA PASS`, before `git push` and before any deploy.

---

Role: You are verifying that "{{PROJECT_NAME}}" works for someone who is not you, on a
machine that is not this session.

The failure this gate exists to catch: the product works in the agent's session and
nowhere else. It depends on a file that was never committed, a variable that lives only
in this shell, a service someone started by hand, or a migration that was applied
directly to a database. Everything is green and nothing is reproducible.

## Task — verify each item by running it, not by reading

### 1. Clean checkout starts
Clone or copy the repository into a **fresh directory**, install from the committed
lockfile, and start the product with `{{RUN_COMMAND}}`.

- [ ] Install succeeds from the lockfile alone
- [ ] Product starts and serves a first request / renders a first screen
- [ ] Nothing had to be created by hand to make it start

Anything you had to do manually is a missing artifact. Add it to the repo or to
`docs/surprises.md` — do not carry it in your head.

### 2. Configuration is complete
- [ ] `.env.example` lists every variable the product actually reads
- [ ] No real secret is committed anywhere in the diff or in the repo
- [ ] Starting without optional variables fails with a clear message, not a stack trace

Grep the source for environment reads and compare against `.env.example`. A variable the
code reads but the example omits is the single most common "works only for the author"
defect.

### 3. Data changes are reversible
Only when the phase touched a schema, migration, or persistent data:

- [ ] Migration runs on an empty database
- [ ] Migration runs on a copy holding realistic existing data
- [ ] The documented rollback (`{{ROLLBACK_COMMAND}}` or the migration's own down step)
      restores the previous state
- [ ] Destructive steps are named explicitly in the release notes

### 4. The product reports its own health
- [ ] A health or readiness check exists and answers when the product is up
- [ ] Errors reach a log the owner can read after the fact — not only the console
- [ ] Starting the product produces no unexplained error or warning

### 5. Smoke path
Run the single most valuable end-to-end scenario from the PRD, start to finish, on the
clean checkout. Record what you observed at each step.

## Output Format

```markdown
# Release Check — {{PROJECT_NAME}}, {{CURRENT_DATE}}

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Clean checkout starts | ✅ / ❌ / ➖ n/a | command + observed output |
| 2 | Configuration complete | | |
| 3 | Data changes reversible | | |
| 4 | Health and logging | | |
| 5 | Smoke path | | |

## Manual steps that were required
| Step | Why it was needed | Where it is now recorded |
|------|-------------------|---------------------------|

## Verdict
RELEASE READY | RELEASE BLOCKED: <what fails> | RELEASE UNKNOWN: <what could not be checked>
```

## Constraint — this gate never ships anything

You verify and report. You do **not** push, deploy, publish, or run anything against a
production or shared environment. Every check runs locally or against a disposable
target you created for the check.

The owner reviews the diff and performs the outward-facing action. Ask for explicit
permission before any command that reaches outside this machine — that permission covers
one action, not the rest of the session.

## Progress Tracking

Record the verdict in `PROGRESS.md`. Log anything deferred in
`docs/tech-debt-tracker.md`, and anything surprising in `docs/surprises.md`.
