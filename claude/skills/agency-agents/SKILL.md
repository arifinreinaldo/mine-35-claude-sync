---
name: agency-agents
description: Install a curated, stack-matched set of Agency Agents into a project's .claude/agents/. Use when the user asks to initialize, add, refresh, or audit agency agents for a repo — or says "agency agents", "init agents", "which agents for this project".
---

Install a small set of agent personas from The Agency roster into the **current project**, matched to the stack that the project actually uses.

Project scope is deliberate. Agents in `~/.claude/agents/` load their name and description into every session's system prompt. The full 268-agent roster costs about 17k tokens per session. A 10-agent project set costs under 1k, and only in the repo that needs it.

## Constants

- Roster repo: `C:/Users/Reinaldo/Backend/agency-agents`
  If that path is missing, ask the user where the clone lives. Do not clone it.
- Install target: `<project-root>/.claude/agents/`
- Marker in project `CLAUDE.md`: the literal string `agency-agents`

## Step 1 — Read the marker BEFORE anything else

```bash
grep -n "agency-agents" CLAUDE.md 2>/dev/null
```

**No match, or no CLAUDE.md** → the project is not initialized. **STOP and ask the user:**

> This project has no Agency Agents set. Initialize one? I detected `<stack>` and would install `<N>` agents into `.claude/agents/`.

Wait for the answer. Do not copy files before the user agrees.

**Match found** → the project is initialized. Read the roster listed under the marker, then go to Step 5 to reconcile. Do not ask again.

## Step 2 — Detect the stack

Run one pass. Each hit adds agents in Step 3.

```bash
ls pubspec.yaml composer.json package.json go.mod build.gradle build.gradle.kts \
   Dockerfile docker-compose.yml requirements.txt pyproject.toml 2>/dev/null
ls -d postman supabase migrations database llm_wiki .github/workflows 2>/dev/null
```

Read `composer.json` and `package.json` when present. The dependency names decide the framework, not the file's existence.

## Step 3 — Map signals to agents

Paths are relative to the roster repo. Copy files by path. **Never use `install.sh --agent`** — it resolves slugs with one subprocess per roster file and takes over 3 minutes for 2 agents on Windows Git Bash.

**Core — always install (5):**
```
engineering/engineering-code-reviewer.md
engineering/engineering-minimal-change-engineer.md
engineering/engineering-codebase-onboarding-engineer.md
testing/testing-reality-checker.md
testing/testing-evidence-collector.md
```

**Stack adds:**

| Signal | Add |
|---|---|
| `pubspec.yaml` | `engineering/engineering-mobile-app-builder.md`, `engineering/engineering-mobile-release-engineer.md` |
| `build.gradle*` and no `pubspec.yaml` | `engineering/engineering-mobile-app-builder.md`, `engineering/engineering-mobile-release-engineer.md` |
| `composer.json` with `laravel/framework` | `engineering/engineering-senior-developer.md`, `engineering/engineering-backend-architect.md` |
| `composer.json` with `filament/filament` | `engineering/engineering-filament-optimization-specialist.md` |
| `package.json` with `react`, `vue`, `next`, or `svelte` | `engineering/engineering-frontend-developer.md` |
| `go.mod` | `engineering/engineering-backend-architect.md`, `engineering/engineering-sre.md` |
| Any JSON API route or `docs/api-standard.md` | `engineering/engineering-api-platform-engineer.md` |
| `postman/` or an OpenAPI file | `testing/testing-api-tester.md` |
| `migrations/`, `supabase/`, or `*.sql` | `engineering/engineering-database-optimizer.md` |
| `Dockerfile`, `docker-compose.yml`, or `.github/workflows/` | `engineering/engineering-devops-automator.md` |
| Playwright or Cypress config | `testing/testing-test-automation-engineer.md` |
| Auth, session, or token code | `security/security-appsec-engineer.md` |
| `.env` committed, or secret handling code | `security/security-secrets-credential-engineer.md` |
| Stripe, PayMongo, or billing code | `engineering/engineering-payments-billing-engineer.md` |
| `llm_wiki/` | `engineering/engineering-knowledge-graph-engineer.md` |

**Cap the set at 12.** More agents dilute selection and cost tokens. When a project trips more than 12 rules, drop the weakest matches and say which ones you dropped.

Browse the full roster for a signal this table misses:
```bash
bash "$ROSTER/scripts/install.sh" --list agents
```

## Step 4 — Install

```bash
mkdir -p .claude/agents
ROSTER="C:/Users/Reinaldo/Backend/agency-agents"
cp "$ROSTER/engineering/engineering-code-reviewer.md" .claude/agents/
# ...one cp per selected file
ls .claude/agents/
```

Copy, do not symlink. A copy pins the persona, so an upstream edit cannot change a project's agents without review.

## Step 5 — Record the set in project CLAUDE.md

Append this block. It is the marker that Step 1 reads.

```markdown
## Agency Agents

Curated set installed in `.claude/agents/` from The Agency roster
(`C:/Users/Reinaldo/Backend/agency-agents`). Re-run `/agency-agents` to reconcile.

- code-reviewer — review discipline
- minimal-change-engineer — scope control on bug fixes
- ...one line per agent, with the reason it is here
```

On reconcile (marker already present): compare the listed roster against `.claude/agents/`. Copy what is missing, report what is stale, and add newly-triggered agents only after the user agrees.

## Step 6 — Verify

Agents register at session start, so the current session cannot see them. Tell the user:

1. Restart the session, or open a new one. (5 s)
2. Run `/agents` and confirm the project agents are listed. (10 s)

**Known risk:** 264 of 268 roster files carry a spaced, title-case `name:` (`name: Code Reviewer`). Claude Code documents `name` as a lowercase-hyphen slug. If `/agents` does not list an installed agent, slugify the frontmatter in place:

```bash
for f in .claude/agents/*.md; do
  awk 'NR<=10 && /^name: /{s=tolower(substr($0,7)); gsub(/[^a-z0-9]/,"-",s); gsub(/--+/,"-",s); sub(/^-/,"",s); sub(/-$/,"",s); print "name: " s; next} {print}' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
```

## Do not

- Do not install to `~/.claude/agents/`. That taxes every session in every repo.
- Do not install the whole roster or a whole division "to be safe".
- Do not run `install.sh --agent`. It is unusably slow on Windows.
- Do not commit the project `.claude/agents/` or the CLAUDE.md edit unless the user asks.
