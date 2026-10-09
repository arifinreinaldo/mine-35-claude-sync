---
name: plan-execution-new
description: Builds a feature in phases from a Sonnet main session - Opus plans (pipeline-planner) and reviews, Haiku or Sonnet executes each step by size and label, with an optional UI design gate and spec review. Use for a non-trivial feature or multi-file change. Skip for trivial edits and bug diagnosis.
---

# Plan-Execution (Sonnet main)

Main session (Sonnet) orchestrates. Use the Agent tool's `model:` override. Never ask for a `/model` switch.

## Flow

1. **UI design gate** (major UI changes only) — follow `ui-design.md`: tone scores, distinct directions, one comparison page, the user's choice. Pass the chosen direction to the planner. Skip for tweaks and for screens syscon config already renders.
2. **Plan** — spawn `pipeline-planner` (Opus) with the goal, constraints, and any UI direction. It returns the spec as text. Save it to `docs/<feature>-spec.md` yourself, then read it. Decode HTML entities (`&lt;`, `&gt;`, `&amp;`) if any came through.
3. **Spec review** — follow `spec-review.md`: the Ponytail pass on every spec, plus one Opus reviewer for contract / 3+ file / live-state / security specs. Amend the spec for the findings the user accepts.
4. **Confirm** — show the user the spec and wait. Execution is the expensive phase to redo.
5. **Route** — assign every step a model with the table below.
6. **Execute** — spawn `pipeline-executor` with `model:` per group. Batch adjacent steps with the same model into one call. Name the off-limits files in the brief.
7. **Verify** — run each step's `verify` and the spec's overall `verify` yourself. Show the output.
8. **Review** — follow `code-review.md`. For major UI changes, also apply the reality-check and reduction pass in `ui-design.md`.
9. **Fix** — an accepted finding goes back to `pipeline-planner` to amend the plan, then re-run only the affected steps. Never loop the executor on its own.

## Routing table

| Step | Runs on |
|---|---|
| `exec: mechanical` AND every edit <= 2 lines AND no new file, 2+ such edits in the batch | Haiku (`pipeline-executor`, `model: haiku`) |
| Lone `mechanical` edit <= 2 lines | Main session edits directly (a spawn costs more than the edit) |
| Edit >= 3 lines, new file, `exec: judgment`, or unlabeled | Sonnet (`pipeline-executor`, `model: sonnet`) |
| Anything Opus | Plans and reviews only. Opus never executes. |

## Escalation

- Haiku `stopped` and the plan was wrong -> the planner amends the plan.
- Haiku `stopped` on a step labeled `mechanical` where the plan was right -> mislabel. Re-run once on Sonnet and log it.
- Sonnet `stopped` -> the planner (Opus) amends the plan. Opus does not apply the edit.

## Log (reply only, not in the spec)

End the run with one line per step: step, model used, applied/stopped/mislabel. If more than ~20% of Haiku steps stopped or were mislabeled, say so and propose turning Haiku off for this project.

## When not to use this

Single-file bug fixes, renames, typos, anything under the plan-mode threshold. The spec costs more than the work. Write the code. Also skip the execute spawn when the build is under roughly a hundred lines with no repetition: plan, build inline, still review.

## Known Blockers

- Planner overrates steps as `mechanical`: the log above is the detector.
- The planner has no Write tool, so the spec comes back inline and the main session saves it. HTML entities in it must be decoded by hand.
- Ported from the deprecated `plan-execution` (kept in `skills/.trash/`). Fable reviewers were dropped on purpose, so spec and code review are Opus only and lose model diversity.
- Unverified: the `skills/.trash/` copy keeps `name: plan-execution`. If it loads as a skill, the old version is still live.

## Changelog

- 2026-10-09: created.
- 2026-10-09: ported UI design gate, spec review and code review from `plan-execution`, Opus only.
- 2026-10-09: UI gate moved before planning; escalation unified with `haiku-ladder` (Haiku -> Sonnet -> planner amends); Ponytail pass added to spec review.
