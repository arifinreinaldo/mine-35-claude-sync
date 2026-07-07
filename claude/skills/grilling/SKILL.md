---
name: grilling
description: Interview the user relentlessly about a plan or design. Use when the user wants to stress-test a plan before building, or uses any 'grill' trigger phrases.
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a question can be answered by exploring the codebase, explore the codebase instead.

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
