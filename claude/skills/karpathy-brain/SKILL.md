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

1. Confirm it's a git repo (offer `git init` if not — the wiki must be versioned with the code).
2. Detect the stack from manifests present: `pubspec.yaml`, `composer.json`, `package.json`, `build.gradle(.kts)`, `Cargo.toml`, `go.mod`, `*.sln`, `Gemfile`, `requirements.txt`/`pyproject.toml`.
3. Copy every file from this skill's `templates/` into the project's `llm_wiki/`, replacing placeholders (`{{PROJECT_NAME}}`, `{{DATE}}`, `{{STACK}}`, `{{ENTRYPOINTS}}`). `{{DATE}}` = `date +%F`.
4. **Seed pass (read-only, shallow):** manifests, `README*`, the top-level directory listing, and entry points (`main.dart`, `lib/main.*`, `routes/*.php`/`index.php`, `*Application.kt`/`MainActivity.kt`, `main.go`, `src/index.*`). From that, fill:
   - `architecture.md` — system shape, entry points, primary data flow (one pass, no deep dive).
   - `code_map.md` — one row per top-level dir: path → purpose → page (`TBD` until a room exists).
   - `map.md` — route the four intents to whatever pages exist; mark `areas/*` as "expand on demand."
5. **Wire search:** take `templates/project-CLAUDE.md`. If the project has a `./CLAUDE.md`, append it as a guarded `## llm_wiki (memory palace)` section (skip if already present); else create `./CLAUDE.md` from it.
6. Commit to the **project** repo: `docs: scaffold llm_wiki memory palace`. Ask before push.

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
7. Commit to the project repo: `docs: sync llm_wiki for <change>` (Conventional Commits). Ask before push.

## Operation: lint (health check)

On request, or scoped after `update`:

- **Orphans:** pages not reachable from `map.md`/`index.md`.
- **Stale paths:** `code_map.md` rows pointing at files absent from `git ls-files`.
- **Coverage gaps:** top-level dirs with no `code_map.md` row.
- **Contradictions / broken `[[links]]`** across pages.

Report concisely; fix the cheap ones, flag the rest.

## Anti-patterns

- ❌ Reading every file in `llm_wiki/` to "build context" — read `map.md`, then only what it routes you to.
- ❌ Deep-crawling the whole codebase at init — seed shallow; rooms fill on demand.
- ❌ Letting the wiki drift — an out-of-date page is worse than no page. `update` is not optional after a change.
- ❌ Stamping the wiki into a non-git dir — it must be versioned with the code.
- ❌ Answering from training knowledge when the wiki covers it — the wiki overrides general knowledge for this repo.

## Relationship to existing setup

- The per-project search habit lives in each project's `CLAUDE.md` (written by `init`), not in global config.
- For the flutter_rad syscon domain specifically, [[syscon-lookup]] is the specialized router; this skill is the generic engine and bootstrapper.
