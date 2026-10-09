# Spec Review (Phase 1b)

Adapted from pstack `interrogate` + `blast-radius`. Runs after the spec is written, before you
confirm it and before any Phase 2 dispatch.

## When

- **Two-model review:** the spec touches a contract (API, schema, public signature), 3+ files,
  live state, or a security boundary.
- **Otherwise:** one Opus reviewer. Same prompt, one subagent.
- Under the "skip Phase 2" threshold and no contract change: skip Phase 1b.

## Dispatch

Launch both reviewers in ONE message. `subagent_type: Explore` (read-only), `run_in_background: true`.

| Reviewer | `model` |
|---|---|
| A | `opus` |
| B | `fable` |

Same filled prompt to both. Diversity comes from the models, not from assigned personas.
Prompt carries: one paragraph of intent, the spec path, the rubric below, and the
return format.

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

## Synthesize (main session, Opus)

You are the lead, not an aggregator.

- Findings raised by both models = highest signal. Lone-model findings still get read.
- Merge duplicates; note which model raised each. Record explicit disagreements.
- Bucket each: **Act on** (would block a real PR), **Consider** (tradeoff for the user),
  **Noted** (valid, low impact), **Dismissed** (wrong or missing context — one-line why).
- Present the buckets to the user. Do not auto-apply. Amend the spec for the "Act on" items the
  user accepts, then continue to the existing "confirm the spec" step.
