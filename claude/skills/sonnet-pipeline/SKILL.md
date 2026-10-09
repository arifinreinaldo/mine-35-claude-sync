---
name: sonnet-pipeline
description: Use for a non-trivial feature or multi-file change when the main session is Sonnet - Opus plans (pipeline-planner), Haiku or Sonnet executes per step by size and label, Opus reviews (pipeline-reviewer). Skip for trivial edits and for bug diagnosis.
---

# Sonnet Pipeline

Main session (Sonnet) orchestrates. Use the Agent tool's `model:` override. Never ask for a `/model` switch.

## Flow

1. **Plan** — spawn `pipeline-planner` (Opus). Give it the goal, constraints, and the spec path (`docs/<feature>-spec.md`). Read the spec.
2. **Route** — assign every step a model with the table below.
3. **Execute** — spawn `pipeline-executor` with `model:` per group. Batch adjacent steps with the same model into one call.
4. **Verify** — run each step's `verify` and the spec's overall `verify` yourself. Show the output.
5. **Review** — spawn `pipeline-reviewer` (Opus) on the diff + spec.
6. **Fix** — a finding goes back to `pipeline-planner` to amend the plan, then re-run only the affected steps. Never loop the executor on its own.

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

## Known Blockers

- `CLAUDE_CODE_SUBAGENT_MODEL`, if set, may override the per-call `model:`. Leave it unset.
- Planner overrates steps as `mechanical`: the log above is the detector.

## Changelog

- 2026-10-09: created.
