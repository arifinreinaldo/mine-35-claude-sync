# {{PROJECT_NAME}} — llm_wiki map (floor plan)

> **Read me first.** Tell me your intent; I route you to the 1–3 pages you need. Don't read the whole wiki.
> Stack: {{STACK}} · Seeded: {{DATE}}

## Intent → pages

### Learn / Onboard — "I'm new here, how does this work?"
- Start: [[architecture]] → [[conventions]]
- Add onboarding rooms under `areas/` as they're written.

### Build / Generate — "I'm adding a feature/screen/endpoint"
- [[conventions]] (patterns to follow) → the relevant `areas/<feature>`
- Cross-reference code via [[code_map]].

### Debug / Fix — "something's broken / behaves wrong"
- [[code_map]] (which file owns this?) → the owning `areas/<feature>` page
- [[architecture]] for data-flow / timing questions.

### Understand — "how does X actually work end to end?"
- [[architecture]] → follow [[code_map]] into the rooms.

## Always
- New area with no room yet? Create `areas/<slug>.md`, then link it here and in [[index]].
- After changing code, run the `karpathy-brain` **update** op before you forget.
