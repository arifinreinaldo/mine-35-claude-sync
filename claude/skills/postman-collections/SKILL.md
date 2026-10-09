---
name: postman-collections
description: Use when creating or updating a Postman collection or environment, writing pm.* scripts, or running newman. Covers self-contained collections, variable scope, and webhook signing.
---

# Postman Collections

Self-contained at project level: the collection lives in the repo it exercises (`postman/`, committed — never only in a personal Postman workspace), and every variable it uses is declared in that collection's own `variable` block with a working default. Importing that one file runs green with no environment selected. Secrets stay empty there (collections get committed) — pass at run time with `--env-var`. An environment file is optional and wins when selected (Postman resolves environment → collection); namespace variables per feature (`paymongo*`, `duitNow*`) so one shared environment can serve every collection.

In scripts: read with `pm.variables.get()`, never `pm.environment.get()` (environment scope only → `undefined` standalone); write with `pm.environment.set()` (newman gives an ephemeral environment even without `-e`); declare with `var` inside an IIFE, never top-level `const`/`let` (newman shares one sandbox scope across requests → "already been declared"). Sign a webhook body by building it in a pre-request script and sending only `{{thatVar}}` — a body containing `{{...}}` is substituted after signing, so the bytes signed stop matching the bytes sent. A `{{var}}` inside a script stays literal — Postman substitutes only the request URL, headers, and body. Resolve it with `pm.variables.replaceIn('{{var}}')`; never write `{{var}}` into a regex or a comparison. Verify with `newman run` **both** with and without `-e`; each of these fails in only one of the two modes.

## Changelog

- 2026-10-09: moved verbatim from global CLAUDE.md so it loads only on Postman work.
