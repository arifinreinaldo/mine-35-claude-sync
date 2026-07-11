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
