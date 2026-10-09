# Code Review (Phase 3)

Adapted from pstack `interrogate` + `blast-radius`. Review is against the spec first, taste never.

## When

- **Two-model review + blast-radius pass:** same trigger as `spec-review.md` (contract change, 3+
  files, live state, security boundary).
- **Otherwise:** one Opus reviewer, existing Phase 3 checklist only.

## Dispatch

Launch in ONE message, `subagent_type: Explore`, `run_in_background: true`:

| Reviewer | `model` |
|---|---|
| A | `opus` |
| B | `fable` |

Same prompt to both: spec path, changed files (or `git diff <base>...HEAD`), Phase 2's verbatim
check output, and the order below. Style the spec did not ask about is noise — say so in the brief.

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

## Blast-radius pass (one extra Opus subagent, same trigger)

Find what the change breaks beyond the diff, where grep stops: JSON an API returns, DB columns,
wire formats, feature flags, code three hops away.

- Name the ONE fact the change is safe because of.
- Prove it by running real code (a small script or test that fails loud if wrong). If it cannot be
  proven cheaply, mark it **unproven** — never write it up as settled.
- Return: what it does, the safety fact and how far it was proven, real risks with `file:line`,
  what was checked and cleared, and the cheapest repro before merge.

## Synthesize (main session, Opus)

Same rules as `spec-review.md`: consensus first, lone findings read, disagreements recorded,
buckets Act on / Consider / Noted / Dismissed with a one-line rationale each. Do not auto-apply.
Send "Act on" items back to a Sonnet subagent as a fix brief, then go to Phase 4 — re-run the
acceptance check yourself.
