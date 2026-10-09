---
name: herdr-notify
description: Use when a long-running script (build, deploy, upload, migration) should show live progress on its Herdr tab and notify when it finishes — "notify herdr when done", "show build progress in herdr", "tab badge", "add herdr status to this script". Requires HERDR_ENV=1; no-ops elsewhere.
---

# Herdr notify

Gives a script two signals inside Herdr: a **tab status** (working / Done / blocked, with a detail message) and a **finish toast** with the finish time.

## Facts (verified on herdr 0.9.3)

- Tab status comes from `herdr pane report-agent <pane> --source ID --agent LABEL --state idle|working|blocked --message TEXT`. `idle` shows as a Done badge when the tab is unseen.
- `herdr notification show <title> --body TEXT --sound done|request` is only a toast. Herdr suppresses it for the **active** tab, and it never sets a tab badge.
- `herdr pane report-metadata --title` sets display text only; it does not drive status.
- `Process.run` buffers output. Live pane output needs `Process.start`; status and toast do not.
- Target the script's own pane with `$HERDR_PANE_ID`. Skip when `pane get` shows another agent (for example `claude`) owns it.

## Reference implementation

`tool/herdr_status.dart` in flutter_rad_pvmi. Copy it into the target project's tool dir. API:

| Call | Effect |
|---|---|
| `herdrBuilding('devLocal 1/4')` / `herdrBuilding(null)` | tab message `building devLocal 1/4` |
| `herdrUpload('demoSales', true/false)` | adds/removes `uploading demoSales`; several can run at once |
| `announceFinish(what, ok:, took:)` | logs `✓ <what> finished at HH:MM:SS (took M:SS)`, sets `idle`/`blocked`, shows the toast |

Wired in `tool/build_apk.dart` (single + batch + background uploads) and `tool/deploy_play_store.dart`.

## Wiring rules

1. Call `herdrBuilding` before each build step and `herdrBuilding(null)` after it.
2. Call `herdrUpload(x, true)` before an upload and `false` after it.
3. Call `announceFinish` on **every** exit path, including `exit(n)` failures. Await it before `exit`.
4. Keep every `herdr` call best-effort (`try/catch`). A status badge must never fail the build.
5. Do not run `herdr` from a non-Herdr shell; the helper checks `HERDR_ENV`.

## Verify

1. In a plain pwsh pane run the script, then switch to another tab. Expect a working badge with the detail message, then Done.
2. Quick check without a build: `herdr pane report-agent <pane> --source t --agent build --state working --message x` then `herdr pane get <pane>`.

## Known blockers

- Not confirmed: whether the sidebar draws a Done badge (status value is confirmed via `pane get`).
- After the run the pane stays labelled agent `build`, state `idle`. Release it with `herdr pane release-agent <pane> --source tool_status --agent build` if that bothers you.

## Changelog

- 2026-10-09: created from build_apk.dart / deploy_play_store.dart wiring.
