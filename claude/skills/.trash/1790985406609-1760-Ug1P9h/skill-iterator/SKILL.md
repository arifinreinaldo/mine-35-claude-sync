---
name: skill-iterator
description: Critique any existing skill by fanning out N parallel reviewer agents, each with a distinct lens and fresh context. Returns a ranked, deduplicated improvement list with severity. Triggers on phrases like "review this skill", "iterate on the skill", "critique this skill", "find improvements in skill", "stress test the skill", "harden this skill", "skill audit", "skill review pass". Designed for skill authors who want adversarial review without anchoring bias.
---

# Skill Iterator

## Purpose

Take an existing skill and find what's wrong with it — by deploying many independent reviewers, each blind to the others, each through a different lens. This neutralizes single-reviewer anchoring and surfaces blind spots one author can't see alone.

This skill **does not write code or fix the target skill**. It produces a triage list. The author decides what to apply.

## When to invoke

- Yu says "review skill X", "iterate on the skill at path P", "critique skill", "stress test my skill", "skill audit", "find improvements in <skill>"
- Before promoting a v1 skill to "real use"
- After 4–6 weeks of live use, to harden a v1 into v2
- Whenever a skill governs real-money or high-stakes decisions

## Inputs (ask up front, use AskUserQuestion)

1. **Path to the target SKILL.md** — absolute path. Required.
2. **Number of reviewers** — default 15. Min 5, max 25. More reviewers = wider coverage but slower.
3. **Lens set** — choose from "default 15-lens stack" or "custom" (paste comma-separated lens names).
4. **Severity bar for output** — "all findings" or "high+critical only".

If any of these are obvious from context (path already provided, severity stated), skip the question for it.

## The default 15-lens stack

Each lens runs as one independent reviewer agent. Lenses cover orthogonal failure modes — don't drop lenses lightly, they were chosen to minimize overlap.

| # | Lens | What it hunts |
|---|---|---|
| 1 | Statistical rigor | Lookahead bias, p-hacking, in-sample/out-of-sample mixing, sample size |
| 2 | Risk management | Gap risk, sizing-vs-volatility, drawdown control, cluster correlation |
| 3 | Data fragility | Gated endpoints, fallback consistency, provenance, cache staleness |
| 4 | Execution feasibility | Context blowup, fan-out, batching, resumability, checkpointing |
| 5 | Survivorship/selection bias | Features fit to known winners, no held-out, no near-miss class |
| 6 | Edge cases | Halts, splits, M&A, FDA, lockup, dilution, going-concern, delisting |
| 7 | Output usability | Cold-start outputs, missing diffs, no decision prompts, friction at use-time |
| 8 | False positive | What trash slips through? — fraud, dilution zombies, shell companies |
| 9 | False negative | What real wins are excluded? — momentum continuation, breakouts, accelerators |
| 10 | Market regime sensitivity | Bull-only logic, no VIX adjustment, no regime gate |
| 11 | Cost/slippage | Spread/fees eating the edge, ADV-based sizing, liquidity gates |
| 12 | Behavioral/psychology | Tilt failure modes, revenge-action, missing cooldowns, override mechanisms |
| 13 | Maintainability | No outcome log, drift detection, fixture rotation, version mechanism |
| 14 | Catalyst/scope breadth | Only one trigger type caught; orthogonal triggers ignored |
| 15 | Validation/test design | Insufficient fixtures, no held-out, no hard-class coverage, retrospective contamination |

These map cleanly to most decision-support skills (trading, screening, research, ops checklists). For pure document-creation skills (pptx, docx), swap lenses 2, 10, 11, 12 for: **accessibility**, **template fidelity**, **i18n / locale**, **export reliability**.

## Workflow when invoked

### Step 1 — Confirm inputs (AskUserQuestion)
Ask for path, reviewer count, lens set, severity bar. Stop if path doesn't resolve to a real file.

### Step 2 — Read the target skill
`Read` the SKILL.md once yourself. Note: filename, line count, sections, declared purpose. This is for the consolidation step, NOT for the reviewers — reviewers must read it blind.

### Step 3 — Fan out reviewers in ONE message
Single message, N `Agent` tool calls in parallel. Each agent gets:

- The exact absolute path to the target SKILL.md
- Two-sentence context about what the skill does (from your read in Step 2 — keep neutral, don't lead the witness)
- The single lens this reviewer must apply
- A strict template for the response:
  - (1) The problem — cite the section/line
  - (2) The fix — concrete, implementable
  - (3) Why it matters — what breaks without it
- Word cap: 150 words per reviewer

**Critical:** each agent gets ONE lens only. Do not let them roam. Roaming = noise.

### Step 4 — Consolidate
Collect the N returns. Build a single table sorted by severity:

```markdown
| # | Lens | Core problem | Fix (1-liner) | Severity |
```

Severity ladder:
- **CRITICAL** — silent failure that loses money / corrupts output / produces overconfident wrong answers
- **HIGH** — degrades accuracy meaningfully, or makes the skill unrunnable in common conditions
- **MEDIUM** — quality-of-life, drift over time, or non-critical edge cases
- **LOW** — cosmetic, redundant with other findings

Severity is the reviewer's call, but you cross-check: if two reviewers flag the same root cause (e.g., "survivorship" and "validation" both ding the same fixture problem), fold them into one row and note the duplicate count — the duplication is itself a signal that this finding is real.

### Step 5 — Output (Markdown file)

Save to `/outputs/skill-review-{skill-name}-{YYYY-MM-DD}.md` with sections:

1. **Target & context** — what skill was reviewed, when, lens count.
2. **Headline** — one paragraph: how many critical / high / medium, and the top 3 most important findings to fix first.
3. **Ranked findings table** — the full deduplicated list.
4. **Lens coverage report** — which lenses fired which severity. Lenses that returned "nothing significant" = either the skill is sound on that axis OR the lens is wrong for this skill type — call this out, don't hide it.
5. **Reviewer-by-reviewer raw responses** — collapsed/footnoted, for audit.
6. **Suggested next step** — three options for the author:
   - (A) Apply top-3 critical fixes now (you can ask the author and do it in the same session if they pick this)
   - (B) Triage further — author manually picks which findings to apply
   - (C) Defer — log findings, revisit after live-run period

### Step 6 — Offer to apply fixes
After the report, ask the author: "Want me to apply the top critical fixes to your skill now, or leave the review as a triage doc?" If yes, edit the target SKILL.md with surgical Edit calls — one finding at a time, each with a clear commit-style description.

## Quality rules for the reviewers

These are non-negotiable instructions baked into each reviewer prompt:

1. **Read the file before you opine.** No findings based on the description alone.
2. **One concrete finding only.** Reject "needs more rigor in general" — name the section and the line.
3. **Cite the section/line you're criticizing.** No fix is acceptable without a pointer to what it replaces.
4. **No proposing new lenses.** Stay in your lens. Other reviewers cover other lenses.
5. **No "you should do everything better."** If the lens doesn't apply, say so and stop. (Better to return "no significant finding through this lens" than to manufacture one.)
6. **150 word cap.** Brevity forces clarity.
7. **Do not collaborate.** No SendMessage to other reviewers. Each agent is independent.

## Anti-patterns (what to refuse)

- **Don't run with <5 reviewers.** Below that, you're back to one or two opinions — defeats the point.
- **Don't run on a skill you wrote 30 seconds ago.** Reviewers need something to critique; you need distance to receive critique. Wait at least until v1 is "done."
- **Don't merge fixes without author approval.** This skill produces critique. Application is author's choice.
- **Don't let reviewers fix-then-critique.** Critique only. Application happens later in a different step.
- **Don't accept reviewer responses >300 words.** Long means rambling, rambling means low-signal. Reject and re-run with a stricter cap.

## Example invocation

```
Yu: "review my pre-pop-scanner skill, 15 reviewers, all findings"

Skill-iterator:
1. Confirms path /Users/.../pre-pop-scanner/SKILL.md
2. Reads it once for neutral context
3. Fires 15 parallel Agent calls, one per lens
4. Waits for all returns (~20-60 seconds)
5. Builds consolidated table, deduplicates, severity-ranks
6. Writes /outputs/skill-review-pre-pop-scanner-2026-05-13.md
7. Offers: "Top 3 critical findings — apply now? (A/B/C)"
```

## Token & cost budget

- 15 reviewers × ~22k tokens each ≈ 330k tokens per review pass
- Add ~10k for consolidation
- **Total ≈ 340k tokens per run** — non-trivial. Use 5–10 reviewers if budget-conscious, or for small/simple skills.
- Time: 20–90 seconds wall-clock if agents run truly parallel.

## Lens set variants (for different skill types)

If the target skill is **not** a decision/screening skill, swap lenses 1, 2, 9, 10 for a domain-appropriate set:

**Document-creation skills (pptx, docx, pdf)**:
- Template fidelity, accessibility (a11y), brand consistency, i18n/locale, output reliability across renderers, file-size budget, asset licensing, version compatibility

**Data-pipeline skills (ETL, scraping)**:
- Idempotency, schema drift, rate-limit handling, data-quality assertions, secret leakage, backfill safety

**Communication/outreach skills (emails, slack)**:
- Tone/voice consistency, audience targeting, opt-out compliance, time-zone awareness, A/B testability

If the user's request implies a skill type, infer the right lens set and confirm before fanning out.

## Self-test fixture (to validate this skill works)

When invoked with `--test`:
- Target: `/outputs/pre-pop-scanner/SKILL.md` (this is the pilot case)
- Reviewers: 15
- Expected: ≥3 CRITICAL findings, ≥5 HIGH, no duplicates collapsed into <12 distinct rows
- If output doesn't hit those thresholds, the lens prompts have drifted — recheck the lens definitions.

## Known limitations

1. **Reviewers don't see each other.** Helpful for diversity, but means duplicate findings on the same root cause won't get reconciled by the reviewers themselves — consolidation has to do it.
2. **Lens quality = output quality.** A vague lens ("be critical") returns vague feedback. The 15-lens stack is tuned; deviate only with care.
3. **No live data.** Reviewers can't run the skill — they only read it. Logic bugs that only show up at runtime won't be caught here. Use a separate "live trial" step.
4. **Optimistic on agent independence.** All agents share the same training distribution, so "blind" doesn't mean "truly independent" — there's a hidden correlation floor. Mitigate by varying lens framing explicitly.
5. **Costs scale linearly with reviewer count.** A 25-reviewer run on a long skill can hit 500k+ tokens. Budget accordingly.

## Versioning

This is v1 of skill-iterator. After 3+ real reviews, run it on itself (`skill-iterator --target=skill-iterator/SKILL.md`) and apply the meta-findings. Yes, it should pass its own audit.
