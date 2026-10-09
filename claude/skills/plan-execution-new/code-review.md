# Code Review (step 5)

Adapted from pstack `interrogate` + `blast-radius`. Review is against the spec first, taste never.

## When

- **Full review + blast-radius pass:** contract change, 3+ files, live state, or a security boundary.
- **Otherwise:** `pipeline-reviewer` only, with the order below.

## Dispatch

Launch in ONE message, `run_in_background: true`:

- `pipeline-reviewer` (Opus) — the order below.
- `superexplorer` (Opus, high) — the blast-radius pass. Same trigger only.

The prompt carries: spec path, changed files (or `git diff <base>...HEAD`), the verbatim output of
the verification step, and the order below. Style the spec did not ask about is noise — say so.

## Order

1. Contract drift — the code does something the spec did not say
2. Silent gaps — a spec requirement with no code behind it
3. Correctness on the edge cases the spec named — trace the call chain, do not just flag "could be nil"
4. Root cause vs symptom — a guard clause, retry, or cast that hides a broken invariant
5. Idempotency and ordering — what happens on a second run, or after a crash halfway?
6. Security at the trust boundary — signatures, secrets in logs, injection
7. Verification — do the tests check behavior, and would they fail if the code were wrong?
8. Legacy dual paths — a new path added while the old one stays alive
9. Only then: clarity

## Blast-radius pass

Find what the change breaks beyond the diff, where grep stops: JSON an API returns, DB columns,
wire formats, feature flags, code three hops away.

- Name the ONE fact the change is safe because of.
- Prove it by running real code (a small script or test that fails loud if wrong). If it cannot be
  proven cheaply, mark it **unproven** — never write it up as settled.
- Return: what it does, the safety fact and how far it was proven, real risks with `file:line`,
  what was checked and cleared, and the cheapest repro before merge.

## Synthesize (main session)

Use the same buckets as `spec-review.md`: Act on / Consider / Noted / Dismissed, with a one-line
rationale each. Do not auto-apply. Send "Act on" items to `pipeline-planner` to amend the plan,
then re-run only the affected steps and re-run the acceptance check yourself.
