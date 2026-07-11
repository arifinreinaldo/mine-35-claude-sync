---
name: ground-tooling
description: Establish ground truth for CLI/SDK syntax from the installed tool before writing deploy scripts or integration code. Use when authoring deploy/setup scripts, integration CLI invocations, or SDK integration code — especially version-drift-prone tools (appwrite, wrangler, firebase, gcloud, supabase, artisan, flutter) where remembered syntax may be a version behind. Not for everyday shell commands (git, ls, npm).
---

# Ground Tooling

Before writing any deploy script, integration/setup CLI invocation, or SDK integration, establish ground truth from the **installed** tool — not from memory. CLI command names, flags, and SDK service/method names drift between versions; a confident-but-stale command fails the deploy.

## Order — stop at the first rung that answers you

1. **Pin the version.** `<tool> --version`; for a package, read its `package.json`. Everything below is version-specific — note it.
2. **Interrogate the CLI.** `<tool> --help`, then the subcommand's `--help`. The installed help is authoritative for command names, subcommands, and flags. _(e.g. `appwrite push --help` shows `push tables|buckets|functions` — the old `appwrite deploy collection` is two generations stale.)_
3. **Read the installed SDK's own types.** `node_modules/<pkg>/dist/*.d.ts` (or the language's equivalent) for current service/class/method names and signatures — not remembered ones. _(e.g. `TablesDB` vs `Databases`, `createRow` vs `createDocument`, the real `InputFile` import path.)_ For bundled CLIs, the embedded schema/enums in `dist/` are ground truth too.
4. **Only if 1–3 can't answer:** fetch the tool's current docs — WebFetch the official page, or the `context7` MCP if available. Indexed/web docs can lag the installed binary, so prefer the binary.

Cite what you found (`appwrite push --help` shows …) before writing the command. **Never present a CLI/SDK call as correct if you only remember it.**

## When to use

Deploy scripts, one-command setup, `wrangler`/`appwrite`/`firebase`/`gcloud`/`supabase`/`artisan`/`flutter` invocations, or any SDK integration — especially fast-moving tools where training data may be a generation behind. Skip for tools whose surface you've already verified this session.
