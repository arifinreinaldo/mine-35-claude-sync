---
name: pull-syscon
description: Pull the live syscondb.sqlite (or salesdb/logdb/wmsdb) off an Android device for the flutter_rad project, into a timestamped local snapshot ready for sqlite3 queries. Use when the user asks to inspect, debug, or query the live config / sales / log database — repo files in sample/ and assets/ are seed data, not live state.
---

# pull-syscon

Pulls a live SQLite database from an Android device running the flutter_rad app. Project-specific (flutter_rad) — assumes `adb` is on PATH.

## When to use

The user says any of:
- "check the live syscondb", "look at the real config", "what's actually on the device"
- "debug X form/action/query" (where the answer requires real config rows)
- "pull the salesdb / logdb / wmsdb"

Do NOT use this for: schema questions, action-chain semantics, or generic FieldControl/ActionType lookups — those should go through [[syscon-lookup]] against the wiki first. Only pull the live DB when seed data won't answer the question.

## Variant → package name

flutter_rad uses `{deployment}{Solution}` flavors. Base package is `com.simplr.rad`, with deployment + solution suffixes appended:

| Deployment suffix | Solution suffix |
|---|---|
| `dev` → `.dev` | `app` → `.app` |
| `devon` → `.dev2` | `wms` → `.wms` |
| `demo` → `.demo` | `sales` → `.sales` |
| `play` → `.play` | `local` → `.local` |
| `direct` → (no suffix, uses envPackageName) | |

Common defaults:
- **devLocal** (debug): `com.simplr.rad.dev.local` ← user's default
- **devSales** (debug): `com.simplr.rad.dev.sales`
- **demoSales** (release): `com.simplr.rad.demo.sales`

Custom builds (`isCustomPackage`) read package from `.env.variant` — check `APP_PACKAGE_NAME` if the user is on a client build.

## Procedure

1. **Pick device** — run `adb devices -l`. If multiple devices, ask user which serial; otherwise use the only one. Save serial as `$SER` (use `-s $SER` on all subsequent adb calls).
2. **Pick package** — if user didn't specify, default to `com.simplr.rad.dev.local`. Confirm with user before pulling if any uncertainty.
3. **Pick DB(s)** — default `syscondb.sqlite`. Other valid names: `salesdb.sqlite`, `wmsdb.sqlite`, `logdb.sqlite`.
4. **Pull** — debug builds support `run-as`:
   ```bash
   adb -s $SER exec-out run-as $PKG cat databases/$DB > .claude/snapshots/${DB%.sqlite}_${VARIANT}_$(date +%Y%m%d_%H%M%S).sqlite
   ```
   For release builds (no `run-as`), the device must be rooted: replace `run-as $PKG cat` with `su -c "cat /data/data/$PKG/databases/$DB"`.
5. **Verify** — `sqlite3 <snapshot> "SELECT name FROM sqlite_master WHERE type='table' LIMIT 5;"` to confirm it's a valid DB.
6. **Report** — tell the user the snapshot path. Subsequent `sqlite3 <path> "..."` queries don't need re-pulling.

## Snapshot directory

Snapshots go in `.claude/snapshots/` (project-local, should be gitignored). If the directory doesn't exist, create it. Each snapshot is named `{db}_{variant}_{timestamp}.sqlite` so multiple pulls don't overwrite.

## Gotchas

- **`run-as` only works on debug builds** (`android:debuggable=true`). Release builds need root or `adb backup`.
- **WAL files**: if you see `-wal` / `-shm` companion files in the device's databases dir, pull them too — otherwise queries may miss recent writes. Pulled WAL file goes alongside the main DB with the same base name.
- **Encrypted DBs**: if the project ever adopts SQLCipher, plain `sqlite3` won't open the file. Not currently the case in flutter_rad.
- **Schema reference**: for column/table definitions without pulling, use `llm_wiki/SCHEMA.md` via [[syscon-lookup]].
