---
name: plan-execution
description: Use when building a non-trivial feature end to end — plan on Opus into a markdown spec, execute via a Sonnet subagent, review via an Opus subagent. Skip for trivial or single-file changes.
---

# Plan-Execution

Three phases, three models, one artifact between them. The main session stays on Opus throughout —
subagents carry the other phases. Never ask for a `/model` switch; use the Agent tool's `model:`
override.

| Phase | Who | Output |
|---|---|---|
| 1. Plan | Opus — main session | `docs/<feature>-spec.md` |
| 2. Execute | Sonnet subagent | code + a passing check |
| 3. Review | Opus subagent | findings against the spec |
| 4. Verify | Opus — main session | the check, re-run |

Override any row when I name a different model ("fable review", "haiku for the boring part").
Phase 4 never delegates.

## Phase 1 — Plan

Ground the design first (`/research-gate` if the feature is unfamiliar), then write the spec **to a
file**, not into chat.

Chat does not survive a subagent boundary. The spec is the only channel to Phase 2, so write it for
a competent stranger with no memory of the conversation.

The spec carries, at minimum:

- **Deliverables** — every file to create or touch, and what must stay untouched
- **Contracts** — exact headers, JSON keys, status codes, function signatures
- **Edge cases with their source** — `file:line`, a schema row, or a live API response
- **Acceptance** — the offline check and the live check, as runnable commands

Counterintuitive details are the whole point of writing it down. Anything where a competent guess
lands wrong (`owner_id 1` means nobody; keys are strings not ints; the field is a list not a dict)
gets stated explicitly with where it was verified. Phase 2 will guess otherwise, and guess wrong.

Confirm the spec with me before dispatching. Phase 2 is the expensive one to redo.

## Phase 2 — Execute

Dispatch one Sonnet subagent. Brief it like a colleague who just walked in:

1. **The spec path**, and an instruction to read it fully before writing anything
2. **"The design is decided"** — no redesigning, no extra features, no adjacent improvements
3. **Hard constraints** — the "do NOT touch" list. Stock config files, live databases, live
   third-party state, background daemons. Be specific; a vague boundary gets crossed.
4. **The verification command** it must run itself, with the requirement to iterate until it passes
5. **Return format** — file paths and line counts, the **verbatim** output of the check, every
   deviation from the spec and why, and anything it could not cover

Demand raw output, not a summary of it. "Tests pass" is a claim; a terminal transcript is evidence.

Tell it that reporting partial success honestly is fine and overclaiming is not. It will otherwise
round up.

## Phase 3 — Review

Dispatch an Opus subagent once Phase 2 reports. Give it the spec path and the changed files, and
ask it to review **against the spec** — not against its own taste.

What it looks for, in order:

1. Contract drift — the code does something the spec did not say
2. Silent gaps — a spec requirement with no code behind it
3. Correctness on the edge cases the spec called out by name
4. Security at the trust boundary — signature checks, secrets in logs, injection
5. Only then: clarity

Style disagreements that the spec did not ask about are noise. Say so in the brief.

## Phase 4 — Verify

Run the acceptance check myself. Both subagents' "verified" is a claim, not evidence — Goal-Driven
Execution in CLAUDE.md applies here without exception.

Report which parts I verified and which I did not. If the environment blocks a check, say so and
hand over the exact command rather than calling it done.

## When not to use this

Single-file bug fixes, renames, typos, anything under the plan-mode threshold. The spec costs more
than the work. Write the code.

Also skip Phase 2 when the build is small enough that briefing a subagent costs more than doing it
— under roughly a hundred lines with no repetition. Plan, build inline, still review.

## Known Blockers

- **Planner dispatched as a subagent cannot write the spec if it is the `Plan` agent type.** That
  type is read-only (no Write/Edit), so the spec comes back inline and the main session has to
  save it by hand, decoding HTML entities on the way. When the main session is not on Opus and the
  Plan phase goes to a subagent, dispatch it as `general-purpose` with `model: opus` and name the
  one file it may write.

## Changelog

- 2026-09-03 — Added Known Blockers: Plan-type subagent has no Write tool; use general-purpose +
  model override when the planner runs as a subagent.
