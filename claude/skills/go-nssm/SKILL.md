---
name: go-nssm
description: Use when deploying a Go (or any single-binary) app as an auto-start, auto-restart Windows service via NSSM — "install as a windows service", "run this as a service", "nssm deploy", "keep it running after reboot / after crash", or when a compiled .exe needs supervised background hosting on Windows.
---

# go-nssm — NSSM Windows service deploy for Go apps

## Overview

Package a Go binary as a supervised Windows service using **NSSM** (the Non-Sucking Service Manager). NSSM auto-starts the service at boot, restarts it if it crashes, and captures stdout/stderr to rotating log files — no Go code changes, no `sc.exe` XML wrangling. This skill ships four battle-tested batch scripts plus a vendored `nssm.exe`; you copy them into the target project and change three values.

The scripts encode hard-won Windows gotchas (self-elevation, the ERROR_SERVICE_MARKED_FOR_DELETE race, trailing-backslash path corruption). Reuse them — don't rewrite from scratch.

## When to use

- User wants a Go/compiled app to run as a Windows service (start on boot, restart on crash).
- User says "nssm", "install-service", "keep it running", "deploy on the server".
- Target is Windows. (For Linux use systemd instead — this skill does not apply.)

## What's in this skill

| File | Role |
|---|---|
| `templates/build.bat` | `go build -o <exe> .` |
| `templates/run.bat` | Foreground dev run (build if missing, kill prior instance) |
| `templates/install-service.bat` | Self-elevating install: remove old → install → configure auto-start/restart + log rotation → firewall rule → start → wait for RUNNING |
| `templates/uninstall-service.bat` | Self-elevating stop + remove + firewall cleanup (keeps files/logs) |
| `nssm.exe` | Vendored NSSM (x64). Copy next to the .bat files. |

## How to apply

1. **Copy** all four `templates/*.bat` and `nssm.exe` into the target project root (where `go build .` runs and `.env` lives).
2. **Replace the placeholder tokens** in every copied `.bat`:
   - `__SERVICE__` → the Windows service name, PascalCase, no spaces (e.g. `SimplrMssqlLogger`). Must be identical across all four files.
   - `__EXE__` → the output binary name (e.g. `myapp.exe`). Same in all four files.
3. **Set the port source** in `install-service.bat` (used only for the inbound firewall rule). A `set "PORT=8080"` fallback stays no matter what; the variant block only overrides it when it reads a real port, so a missing `.env` or absent key falls back safely. The template defaults to reading `LISTEN_ADDR=:PORT` from `.env`. If the app takes its port differently, delete the block marked `>>> default variant … <<<` and paste an alternative from the comment above it (`PORT=` key, fixed port, or none). If the app is not a network listener, delete the port block AND the two `netsh` firewall lines.
4. **Gitignore the build output** (`/__EXE__`) but **track `nssm.exe`** — narrow any blanket `*.exe` ignore to just the built binary, or `nssm.exe` won't be committed.
5. Tell the user the deploy flow: run `build.bat`, then right-click `install-service.bat` → the scripts self-elevate. `uninstall-service.bat` removes it.

## Gotchas the scripts already handle (do not "simplify" away)

- **Self-elevation**: NSSM needs admin; each script relaunches itself via `powershell Start-Process -Verb RunAs`.
- **Marked-for-delete race**: an immediate reinstall after remove hits error 1072. The install script polls `sc query` until the old service clears before reinstalling.
- **Trailing-backslash path bug**: `%~dp0` ends with `\`; a `\` before a closing quote escapes the quote and NSSM stores a broken `AppDirectory`. The script strips it.
- **`nssm start` false alarm**: it prints a scary `SERVICE_START_PENDING` while the app is merely still booting. The script uses `sc start` + a `RUNNING` poll instead.
- **English-Windows assumption**: the RUNNING poll greps the literal string `RUNNING`; a localized SKU needs the numeric state code `4`. Flagged in-script.

## Prerequisite the caller must ensure

The app must run correctly from its own folder first (its `.env`/config present, its DB reachable). A service that crash-loops is almost always a missing `.env` or an unreachable dependency — check `logs\err.log`. If the Go app only loads config and exits (no server loop), NSSM will restart-loop it: make sure `main()` actually blocks (serves) before installing.
