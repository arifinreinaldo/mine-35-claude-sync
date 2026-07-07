---
name: my-review
description: Use when the user asks for a code review, architecture review, or to review a PR/branch/feature and wants the personal staged interactive format (not /code-review or ponytail-review).
---

# My Review

Staged interactive review with explicit approval gates.

## Before Starting

- Ask: *1/ BIG CHANGE* (interactive, 1 section at a time, max 4 issues) or *2/ SMALL CHANGE* (interactive, 1 question per section)?
- Do not assume priorities on timeline or scale.
- Pause and ask for feedback after each section.

## Stages

### 1. Architecture
- System design, component boundaries, dependency coupling.
- Data flow, bottlenecks, scaling, security (auth/API boundaries).

### 2. Code Quality
- Organization, module structure, DRY adherence per the "engineered enough" rule (1–2× inline, 3+× extract).
- Error handling gaps, technical debt, engineering balance.

### 3. Testing
- Coverage gaps (unit, integration, e2e) and assertion strength.
- Edge case and failure mode coverage.

### 4. Performance
- N+1 queries, database patterns, memory usage.
- Caching opportunities, high-complexity paths.

### 5. Mobile
- Flutter: bundle size impact, unnecessary rebuilds, widget tree depth.
- State management: pattern consistency (Riverpod/Bloc/Provider — don't mix).
- Platform divergence: Android/iOS behavioral differences in changed code.
- Native plugins: compatibility, null safety, platform channel correctness.
- Assets/images: resolution variants, caching, memory footprint.

## Issue Reporting Format

For every bug, smell, or risk:

1. **Describe:** concrete problem with `file:line` references.
2. **Options:** 2–3 options (including "do nothing").
3. **Details:** effort, risk, impact, maintenance burden for each.
4. **Recommendation:** top choice mapped to my preferences.
5. **Approval:** explicitly ask for agreement before proceeding.

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
