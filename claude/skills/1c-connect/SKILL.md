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
