---
name: 1c-connect
description: Use when the user mentions 1C, 1CI, GES, BSL, infobase, Designer/Configurator, or wants to list, open, or code against their 1C ERP projects/databases from the terminal — in any directory.
---

# 1C Connect

All 1C automation on this Mac goes through one CLI:
`~/VibeProjects/1ci-connector/bin/1c` — never the platform binaries directly.

## Listing projects (always do this first)

```bash
cd ~/VibeProjects/1ci-connector
bin/1c bases      # registered infobases (bases.json) — the "active projects"
bin/1c discover   # Spotlight scan for every file infobase on disk, registered or not
```

These two commands are the ONLY authoritative source for what 1C projects exist.
A folder under `~/1CI/` is not an infobase unless it contains `1Cv8.1CD` —
`discover` checks exactly that; do not infer projects from folder listings.

## Connecting to a base

1. Ask which base if the user hasn't named one.
2. `bin/1c dump <base>` — refresh `src/<base>/` from the live infobase before any
   edit session (the existing tree may be stale). Read-only for the base itself.
3. **REQUIRED:** read `~/VibeProjects/1ci-connector/CLAUDE.md` before editing —
   it is the single source of truth for the edit → check → load pipeline,
   BSL/form XML conventions, and platform gotchas. Do not improvise the workflow.

`bases`, `discover`, `version`, `dump`, `check`, `checkconfig`, `uuidcheck` are
read-only for the infobase; `load`/`dbupdate` overwrite its configuration.

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
