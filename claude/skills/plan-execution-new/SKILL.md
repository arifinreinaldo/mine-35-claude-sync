---
name: plan-execution-new
description: Builds a feature in phases from a Sonnet main session - Opus plans (pipeline-planner) and reviews, Haiku or Sonnet executes each step by size and label, with an optional UI design gate and spec review. Use for a non-trivial feature or multi-file change. Skip for trivial edits and bug diagnosis.
---

# Plan-Execution (Sonnet main)

Main session (Sonnet) orchestrates. Use the Agent tool's `model:` override. Never ask for a `/model` switch.

## Flow

1. **Plan** — spawn `pipeline-planner` (Opus). Give it the goal and constraints. It returns the spec as text. Save it to `docs/<feature>-spec.md` yourself, then read it.
1a. **UI design gate** (major UI changes only) — follow `ui-design.md` before the spec is final: tone scores, distinct directions, one comparison page, the user's choice. The chosen direction goes into the spec. Skip for tweaks and for screens syscon config already renders.
1b. **Spec review** — follow `spec-review.md` (one Opus reviewer for contract / 3+ file / live-state / security specs; skip for small work). Amend the spec for the findings the user accepts.
2. **Confirm** — show the user the spec and wait. Execution is the expensive phase to redo.
3. **Route** — assign every step a model with the table below.
4. **Execute** — spawn `pipeline-executor` with `model:` per group. Batch adjacent steps with the same model into one call.
5. **Verify** — run each step's `verify` and the spec's overall `verify` yourself. Show the output.
6. **Review** — follow `code-review.md`. For major UI changes, also apply the reality-check and reduction pass in `ui-design.md`.
7. **Fix** — an accepted finding goes back to `pipeline-planner` to amend the plan, then re-run only the affected steps. Never loop the executor on its own.

## Routing table

| Step | Runs on |
|---|---|
| `exec: mechanical` AND every edit <= 2 lines AND no new file, 2+ such edits in the batch | Haiku (`pipeline-executor`, `model: haiku`) |
| Lone `mechanical` edit <= 2 lines | Main session edits directly (a spawn costs more than the edit) |
| Edit >= 3 lines, new file, `exec: judgment`, unlabeled, or planner `unsure` | Sonnet (`pipeline-executor`, `model: sonnet`) |
| Anything Opus | Plans and reviews only. Opus never executes. |

## Escalation

- Haiku `stopped` on a mismatch -> the step goes back to the planner to fix. Do not retry on a bigger model.
- Exception: a step labeled `mechanical` that Haiku cannot apply is a mislabel. Re-run it once on Sonnet and log it.

## Log (reply only, not in the spec)

End the run with one line per step: step, model used, applied/stopped/mislabel. If more than ~20% of Haiku steps stopped or were mislabeled, say so and propose turning Haiku off for this project.

## When not to use this

Single-file bug fixes, renames, typos, anything under the plan-mode threshold. The spec costs more than the work. Write the code. Also skip the execute spawn when the build is under roughly a hundred lines with no repetition: plan, build inline, still review.

## Known Blockers

- Planner overrates steps as `mechanical`: the log above is the detector.
- Ported from the deprecated `plan-execution` (kept in `skills/.trash/`). Fable reviewers were dropped on purpose, so spec and code review are Opus only and lose model diversity.

## Changelog

- 2026-10-09: created.
- 2026-10-09: ported UI design gate (1a), spec review (1b) and code review from `plan-execution`, Opus only.
