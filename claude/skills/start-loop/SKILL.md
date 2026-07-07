---
name: start-loop
description: Use when the user states an aim they want pursued repeatedly until done — "start loop", "loop this", "keep going until X", "watch this until Y" — or needs help choosing between /loop, ralph-loop, and /schedule.
---

# Start Loop

Turn a stated aim into the right kind of running loop: interview → classify → spec → confirm → launch.

## Step 1 — Capture the aim

Restate the aim as a **verifiable end condition** — the command, test, or observation that proves "done" (Goal-Driven Execution rule in CLAUDE.md). If the aim has no observable check, that is the first question to ask.

## Step 2 — Targeted questions (max 4, propose-to-clarify)

Anchor each in a proposed default — never a blank questionnaire. Skip any already answered by the aim.

1. **Done-check** — "I'll treat `<command/observation>` passing as done — correct?"
2. **Who moves the state** — my own work (fix/build/write) vs external (CI, deploy, server)? If external: how fast does it actually change?
3. **Stop criteria** — max iterations or timebox. Default: 10 iterations or 2 hours, whichever comes first.
4. **Blast radius** — repo/branch, which files may change, commit policy (commit each green pass; never push without asking).

## Step 3 — Classify the loop

| Situation | Loop type | Launch |
|---|---|---|
| My work moves the state; check runs locally (tests, analyze, build) | Goal loop, self-paced | `/loop <goal prompt>` (no interval) |
| Waiting on external state with a known cadence (CI, deploy) | Fixed interval matched to that cadence | `/loop <interval> <prompt>` |
| Hammer one task continuously in-session until complete | Ralph | `ralph-loop:ralph-loop` |
| No single goal; ongoing tidy-up of pending work | Autonomous | `/loop` (no prompt) |
| Must run while the session/machine is off, or calendar-based | Not a loop — `/schedule` cloud routine | `/schedule` |
| Runs once | No loop — just do the task | — |

Interval guidance: under 5 min keeps the prompt cache warm (cheap ticks); otherwise commit to 20 min+. Avoid ~5–6 min — it pays the cache miss without amortizing it.

## Step 4 — Loop spec (confirm before launch)

Present one block and get explicit OK:

- **Type & interval** — from the table above.
- **Loop prompt** — must contain all four: the end-condition check, "stop the loop when it passes", the iteration/time cap, and what not to touch.
- **Guardrails** — stop criteria, commit policy, escalation rule: "if the same failure repeats 3×, stop and report instead of retrying."

## Step 5 — Launch & handoff

Invoke the `loop` skill with the spec as args. Tell the user how to stop it early (interrupt, or say "stop the loop").

## Red Flags

- Loop prompt without an end condition → runaway loop. Fix before launch.
- Polling something the harness already notifies about (background Bash tasks, workflows) → no loop needed.
- Retrying an identical failing step with no new information → that's the escalation rule's job, not more iterations.

---

## Self-Improvement Protocol

When a blocker interrupts this skill — a step that fails, a missing precondition, or a wrong/ambiguous instruction above — before moving on:

1. **Document** — add a bullet under **Known Blockers**: what you tried, what happened, and the root cause (not just the symptom).
2. **Solve & verify** — apply a fix and confirm it actually works (evidence, not assertion).
3. **Self-improve** — once verified, add a dated line to **Changelog**, then rewrite the affected instruction(s) above so the fix is baked in and the blocker can't recur. Memorialize only reproducible, structural blockers — not one-off transient failures.
4. **Escalate if risky** — if the rewrite is uncertain, high-blast-radius, or changes this skill's core behavior, do NOT self-edit: show the user the proposed change and get review first.

### Known Blockers

_None yet._

### Changelog

<!-- YYYY-MM-DD — blocker → fix -->
