---
name: research-gate
description: Use when planning or researching how to build a non-trivial feature — before writing an implementation plan, in any stack (Laravel, Flutter, Kotlin, SQL, infra). Skip for trivial changes.
---

# Research Gate

Grounded feature research before planning. **Stack-agnostic** — the steps are identical everywhere; only the *grounding sources* change. Output feeds the 4 Invariables check in CLAUDE.md.

## Steps

1. **Discover perspectives** — the 4 Invariables **+** lenses this feature demands (concurrency, migration/back-compat, API contract, failure modes, security, …). Derive from the feature, not a fixed list.
2. **Question per perspective** — what each lens must answer before code is safe.
3. **Answer by grounding** — resolve every question against a *source*, whichever the stack provides:
   - **Code** — the repo (`file:line`).
   - **Framework/library docs** — via Context7 (resolve the lib — Laravel, Flutter/Dart, Kotlin, … — then pull its docs).
   - **Web** — patterns/precedents not in either.
   No ungrounded answers; if one can't be grounded, mark it an **open risk**.
4. **Synthesize → cited brief** — a plan where each decision names its source.
5. **Map unknown-unknowns** — list surfaced constraints/edge-cases; loop 1–4 until a pass adds nothing new.

## Output Contract

Every claim traces to code, a doc, or a flagged unknown — never bare assertion. Mechanizes "never write code you cannot trace invariants for."

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
