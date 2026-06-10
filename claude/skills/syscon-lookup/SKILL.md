---
name: syscon-lookup
description: Answer flutter_rad questions about syscon config tables (FormConfig, ActionConfig, QueryConfig, ListConfig, MenuConfig), FieldControl types, ActionType chains, brick widgets, or server-driven UI behavior by routing through llm_wiki/map.md. Use this FIRST for config questions before reading code or pulling live DBs.
---

# syscon-lookup

Routes config / server-driven-UI questions through flutter_rad's `llm_wiki/`. Project-specific.

## Why this skill exists

flutter_rad has a deep `llm_wiki/` (15+ files, ~100k lines) that mirrors the server-driven config model. Reading the whole wiki burns tokens; reading random files misses cross-references. The map file (`llm_wiki/map.md`) is an **intent router** — you tell it what you want to do, it tells you which 1–3 pages to read.

## Procedure

1. **Always read `llm_wiki/map.md` FIRST.** It's the entry point. Do not skip this even if you think you know the answer.
2. **Match the user's intent** against the router's intent tables:
   - **Learn / Onboard**: new-hire SQL dev questions → `onboarding/*`
   - **Build / Generate**: making new screens/actions/queries → `generation/*`
   - **Debug / Fix**: "button does nothing", "field not showing", "wrong data" → `actions/*` or `config/*`
   - **Understand**: deep model / lifecycle → varies (see map)
3. **Read only the pages the router points to** — do NOT read sibling pages "just in case". The wiki cross-links explicitly when needed.
4. **Cross-reference with code** only after the wiki gives you the relevant table/field/ActionType — then `grep` in `lib/` for handlers (e.g., `ActionConfigBloc`, `brick_view/`).

## When to escalate beyond wiki

| Symptom | Next step |
|---|---|
| Wiki gives you a config-table query but you need actual rows | Use [[pull-syscon]] to grab the live DB |
| Wiki points to code patterns (e.g., a specific handler) | `grep -r "handlerName" lib/bloc/` |
| Wiki entry seems stale vs current code | Read the actual code in `lib/`, then suggest a wiki update |

## Key wiki pages (memorize the slugs, not the contents)

- `map.md` — the router. Always start here.
- `SCHEMA.md` — full DB schema reference for syscondb tables
- `code_map.md` — code → wiki cross-reference
- `index.md` — alphabetical entry list
- `onboarding/start_here.md` — 7-page new-hire path
- `generation/guide.md` — building new screens end-to-end
- `actions/action_chaining.md` — debugging action chains
- `config/queryconfig.md`, `config/formconfig.md`, `config/placeholders.md` — table-specific deep dives
- `ui/theming.md` — color slot / brick theme reference

## Anti-patterns

- ❌ Reading every file in `llm_wiki/` to "build context"
- ❌ Answering from training knowledge without consulting the map (the wiki overrides general Flutter knowledge here)
- ❌ Reading `llm_wiki/archive/` unless explicitly asked (it's historical)
- ❌ Treating wiki as authoritative for live row data — wiki describes the model, not the rows. For rows, use [[pull-syscon]].
