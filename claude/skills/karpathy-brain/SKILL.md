---
name: karpathy-brain
description: Bootstrap and maintain an `llm_wiki/` "memory palace" for a coding project (Karpathy LLM-wiki pattern), so searches route through a map instead of blind grep. Use when initializing a project's wiki/memory palace, wiring its local CLAUDE.md to consult the wiki first, or updating + committing the wiki after a code change. Operations: init, update, lint.
---

# karpathy-brain

Builds and maintains a per-project `llm_wiki/` — an LLM-maintained markdown "memory palace" that sits between you and the codebase, so navigation becomes *walk the floor plan to the right room* instead of grepping blind.

Based on Karpathy's LLM-wiki pattern (raw source → wiki → schema; ingest / query / lint) and his coding principles. Generalizes the `flutter_rad/llm_wiki/` + [[syscon-lookup]] pattern into a reusable initializer.

## Mental model (the memory palace)

| Layer | Here | Rule |
|---|---|---|
| Raw source | the codebase | immutable; the wiki summarizes it, never the reverse |
| Wiki | `llm_wiki/*.md` | LLM-maintained, interlinked; the thing you read first |
| Schema | project `CLAUDE.md` + this skill | defines structure + upkeep |

- `map.md` = floor plan (intent router). `areas/*.md` = rooms. `code_map.md` = address book (code path → room).
- **Search optimization:** read `map.md` → 1–3 target pages. Never read the whole wiki.

## Operation: init

Run when a project has no `llm_wiki/` yet. Scaffold + a shallow seed pass — do NOT deep-crawl every file.

0. **Preflight — never clobber an existing wiki.** If `llm_wiki/` already exists and is non-empty — or the repo already has a similar knowledge base (`docs/wiki/`, `.wiki/`, or a `CLAUDE.md` that already routes through one) — STOP scaffolding. Report what's there and switch to the **update**/**lint** op against it instead. Migrating a different format is opt-in only — ask first. Never overwrite existing wiki files.
0b. **Warrant check — is a wiki even worth it?** Rough heuristic over `git ls-files` filtered to source files: if the repo is **< ~20 code files or < ~2,000 LOC**, it likely fits in a single read — a wiki you must keep in sync is premature. Say so and ask before proceeding (prefer just reading `src/`). This pattern pays off on large, long-lived codebases, not small ones.
1. Confirm it's a git repo (offer `git init` if not — the wiki must be versioned with the code).
2. Detect the stack from manifests present: `pubspec.yaml`, `composer.json`, `package.json`, `build.gradle(.kts)`, `Cargo.toml`, `go.mod`, `*.sln`, `Gemfile`, `requirements.txt`/`pyproject.toml`.
3. Create from this skill's `templates/` **only the files that don't already exist** in `llm_wiki/`, replacing placeholders (`{{PROJECT_NAME}}`, `{{DATE}}`, `{{STACK}}`, `{{ENTRYPOINTS}}`). `{{DATE}}` = `date +%F`. Never overwrite a file that's already there — init is safe to re-run.
4. **Seed pass (read-only, shallow):** manifests, `README*`, the top-level directory listing, and entry points (`main.dart`, `lib/main.*`, `routes/*.php`/`index.php`, `*Application.kt`/`MainActivity.kt`, `main.go`, `src/index.*`). From that, fill:
   - `architecture.md` — system shape, entry points, primary data flow (one pass, no deep dive).
   - `code_map.md` — one row per top-level dir: path → purpose → page (`TBD` until a room exists).
   - `map.md` — route the four intents to whatever pages exist; mark `areas/*` as "expand on demand."
5. **Wire search:** take `templates/project-CLAUDE.md`. If the project has a `./CLAUDE.md`, append it as a guarded `## llm_wiki (memory palace)` section (skip if already present); else create `./CLAUDE.md` from it.
6. Write `llm_wiki/.synced-to` = current `git rev-parse HEAD` + date (the staleness marker — see "Staleness tracking"). Then commit to the **project** repo: `docs: scaffold llm_wiki memory palace`. Ask before push.

Deep `areas/*` pages are created on demand — when a task or an `update` first needs that room.

## Operation: update (after a code change)

The recurring value. Run after finishing any change in a repo that has `llm_wiki/`.

1. `git diff --name-only` (staged + unstaged, or the known changed paths).
2. For each changed file, reverse-look-up `code_map.md` → the affected wiki page(s).
   - Not in `code_map.md`? New territory: add a row; if it's a significant new area, create `areas/<slug>.md` using the room shape in `architecture.md`.
3. **Edit** the affected pages to match the new reality — keep them accurate and DRY; don't just append.
4. Update `map.md`/`index.md` only if intents or structure changed.
5. Append one line to `CHANGELOG.md`: `## <date> — <summary>` + pages touched.
6. Quick `lint` on the touched pages (next section), scoped to what you changed.
7. Rewrite `llm_wiki/.synced-to` = current `HEAD` + date. Then commit to the project repo: `docs: sync llm_wiki for <change>` (Conventional Commits). Ask before push.

## Operation: lint (health check)

On request, or scoped after `update`:

- **Drift (most important):** `git diff --name-only "$(head -1 llm_wiki/.synced-to)"..HEAD -- . ':(exclude)llm_wiki'` — code changed since the last sync means the wiki is behind. Report the lagging files; that's the `update` queue.
- **Orphans:** pages not reachable from `map.md`/`index.md`.
- **Stale paths:** `code_map.md` rows pointing at files absent from `git ls-files`.
- **Coverage gaps:** top-level dirs with no `code_map.md` row.
- **Contradictions / broken `[[links]]`** across pages.

Report concisely; fix the cheap ones, flag the rest.

## Staleness tracking

The wiki is a cache of the code; its value collapses the moment it drifts. `llm_wiki/.synced-to` records the commit SHA the wiki was last reconciled to.

- `init` and `update` write the current `HEAD` into it.
- `lint`'s **drift** check diffs `.synced-to..HEAD` (excluding `llm_wiki/`) — non-empty means the wiki is behind, and names exactly which code files to reconcile.
- **Optional, opt-in:** offer to install a `post-commit` git hook that runs the drift check and reminds when a commit touched code but not `llm_wiki/`. Never install it without asking — it's a per-repo side effect.

## Anti-patterns

- ❌ Reading every file in `llm_wiki/` to "build context" — read `map.md`, then only what it routes you to.
- ❌ Deep-crawling the whole codebase at init — seed shallow; rooms fill on demand.
- ❌ Letting the wiki drift — an out-of-date page is worse than no page. `update` is not optional after a change.
- ❌ Stamping the wiki into a non-git dir — it must be versioned with the code.
- ❌ Answering from training knowledge when the wiki covers it — the wiki overrides general knowledge for this repo.

## Relationship to existing setup

- The per-project search habit lives in each project's `CLAUDE.md` (written by `init`), not in global config.
- For the flutter_rad syscon domain specifically, [[syscon-lookup]] is the specialized router; this skill is the generic engine and bootstrapper.

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
