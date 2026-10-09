---
name: haiku-ladder
description: Use when the main session needs cheap read-only context ("is X there?", "where is Y used?", "gather context on Z", wide file/doc sweeps), or when a decided, mechanical edit plan (renames, repeated pattern edits) can be applied by Haiku. Haiku explores; Opus plans edits; escalate Haiku -> Sonnet -> Opus on failure. Skip for edits without a plan, bug diagnosis, or anything needing judgment.
---

# Haiku Ladder

Use the Agent tool's `model:` override. Never ask for a `/model` switch.

## Triggers (telltales)

Fire this skill when ANY of these is true, before reading files yourself:

- The question is existence or location: "is there", "where is", "which files", "who calls", "does X exist", "find X".
- You are about to run 3+ Grep/Read calls only to collect context for a later decision.
- The user says "explore", "gather context", "sweep", "check the docs for", "haiku", "ladder".
- A plan already exists (spec file or Opus plan) AND every edit in it is mechanical.

Do NOT fire for: bug root-cause, design questions, edits with no plan, anything the user asked you to judge.

## Lane 1 — Read-only (Haiku first)

1. Spawn `Explore` or `general-purpose` with `model: haiku`. Brief: the question, the search scope, and the return format below.
2. Required return: findings, each with `file:line` + a quoted snippet; a `status: done | unsure`; a "not found" list for anything searched and absent.
3. Gate (cheap, mechanical first): spot-check 2-3 cited `file:line` snippets with Read/Grep. A cited line that is missing or says something else = fail.
4. Pass -> use the findings as context. Fail or `unsure` -> rung 2.
5. Rung 2: same brief on `model: sonnet`, plus Haiku's rejected answer and the gate's reason. Same gate.
6. Rung 3: `model: opus`. A failure here goes to the user, no further loop.

Log the rung where each task stopped (one line in the reply). If >30% of tasks leave rung 1, say so and propose starting at Sonnet for that task type.

## Lane 2 — Edits (Opus plans, Haiku applies)

Haiku never decides what to change.

1. Plan first: Opus (main session or `model: opus` subagent) writes exact files, exact edits, and one verification command. No plan = no Haiku edit; use `/plan-execution` or edit directly.
2. Spawn `model: haiku` with the plan. Rules in the brief: apply literally; if a file differs from what the plan expects, STOP and report, never improvise; no extra edits.
3. The main session runs the verification command and shows the output. Haiku does not judge its own edit.
4. Failure goes back to Opus to fix the PLAN. Do not escalate the edit to a bigger model to redo it.
5. Judgment needed while editing? Hand the plan to Sonnet instead (`/plan-execution`).

## Notes

- The user agent `Explore` (`model: haiku`) replaces the built-in. Rung 1 uses it. A per-call `model:` still wins, so rungs 2 and 3 work.
- Rung 3 may use `superexplorer` (Opus, high) instead of a plain `model: opus` spawn.

## Changelog

- 2026-10-09: created. Removed the `CLAUDE_CODE_SUBAGENT_MODEL` blocker: per-call `model:` outranks it since v2.1.251.
