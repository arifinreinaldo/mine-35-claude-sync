# Spec Review (step 3)

Adapted from pstack `interrogate` + `blast-radius`. Runs after the spec is saved, before the user
confirms it and before any execution.

## When

- **Review:** the spec touches a contract (API, schema, public signature), 3+ files, live state,
  or a security boundary.
- **Skip:** small work with no contract change.

## Dispatch

One reviewer: `superexplorer` (Opus, high, read-only), `run_in_background: true`. The prompt carries
one paragraph of intent, the spec path, the rubric below, and the return format.

## Rubric — attack the technical decisions

Review the spec, not the code. Read the code the spec points at before judging it.

1. **Premise** — is this the right problem? Would a smaller change, or no change, meet the goal?
2. **Design space** — name one rejected alternative and why it lost. No alternative considered = a finding.
3. **Contracts** — every header, key, status code, signature is exact and has a stated source.
4. **Edge cases** — each has a `file:line`, schema row, or live response. Unsourced = a guess.
5. **Blast radius** — what else breaks beyond the listed deliverables (JSON consumers, DB columns,
   other languages reading the same bytes, flags, callers three hops out)? Name the ONE fact the
   change is safe because of, and say how sure the spec is of it (said / pointed at a line / walked
   through / ran it). Unproven = say so.
6. **Sequence** — is the work split into units that can each be verified alone? Where is state
   owned, and what order must things run in?
7. **Acceptance** — would the offline and live checks fail if the design were wrong? A check that
   cannot fail is not a check.
8. **Subtract** — anything in the spec no requirement needs.

Return format: per finding — the claim, the spec section or `file:line` that shows it, and
severity (blocks / weakens / nit). Trace failures step by step; "could be wrong" alone is noise.

## Ponytail pass (main session)

Run on every saved spec, even when the Opus review is skipped. Invoke the `ponytail:ponytail` skill and
apply it to the spec: is this the smallest working solution? Which steps can be deleted, merged, or
replaced by something that already exists? Add its findings to the buckets below. Unverified: the
skill is written for code, so judge whether each finding fits a plan.

## Synthesize (main session)

Bucket each finding: **Act on** (would block a real PR), **Consider** (tradeoff for the user),
**Noted** (valid, low impact), **Dismissed** (wrong or missing context — one-line why).
Present the buckets to the user. Do not auto-apply. Send accepted "Act on" items back to
`pipeline-planner` to amend the spec, then continue to "Confirm".
