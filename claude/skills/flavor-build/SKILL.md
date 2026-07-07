---
name: flavor-build
description: Build a flutter_rad APK/ZIP for a specific deployment × solution flavor and mode via tool/build_apk.dart. Use when the user wants to build, package, or deploy a specific flavor like devSales, demoLocal, directWms, playSales, etc.
---

# flavor-build

Wraps `dart tool/build_apk.dart` for flutter_rad's flavor matrix. Project-specific.

## Flavor matrix

Flavor names combine **deployment** + **Solution** (note the capitalized S):

| Deployment | Solution | Mode | Output ext | Example |
|---|---|---|---|---|
| `dev`, `devon`, `demo`, `play`, `direct` | `app`, `wms`, `sales`, `local` | `debug` | `.zip` | `devSales:debug` → `rad-v2-{ver}-devSales.zip` |
| | | `release` | `.apk` | `directWms:release` → `rad-v2-{ver}-directWms.apk` |

Outputs land in `build/app/outputs/flutter-apk/` (renamed) and are also surfaced under `outputs/flutter-apk/` per CLAUDE.md.

## Commands

**Single flavor:**
```bash
dart tool/build_apk.dart --flavor devSales --mode debug
```

**Batch (preferred for multiple flavors):**
```bash
dart tool/build_apk.dart --batch devLocal:debug,demoSales:release,directApp:release
```

**With upload + notify (matches CLAUDE.md `deploy build` shortcut):**
```bash
dart tool/build_apk.dart --batch devLocal:debug,demoSales:release,directApp:release --upload --notify
```

The tool handles: APK signing (via `key.properties`), version bumping, output renaming, optional Google Drive / OneDrive upload, and ntfy notifications.

## Procedure

1. **Confirm flavor + mode** with the user if not specified. Default if user just says "build": ask which flavor.
2. **Check key.properties exists** for release builds: `ls android/key.properties` — release builds will fail without it.
3. **Run via Bash** with appropriate timeout (release builds can take 5–15 min): pass `timeout: 900000` (15 min) for safety.
4. **Surface output path** from the tool's stdout so the user can locate the file.

## Shortcuts (from CLAUDE.md)

- `deploy build` → ask "Deploy devLocal (debug) + demoSales (release) + directApp (release) with upload and notify? (yes/no)" — if yes, run the batch+upload+notify command above.
- `deploy production` → ask "Deploy to Play Store internal track? (yes/no)" — if yes, run `dart run tool/deploy_play_store.dart --track internal`.

## Gotchas

- **`local` solution** is the engineer-only solution (no WMS/Sales-specific assets). Default for devLocal.
- **`direct` deployment** uses `envPackageName` from `.env.variant` and skips the deployment suffix (`.dev`/`.demo`/etc.) — for custom client builds.
- **Output naming**: default builds get renamed to `rad-v2-{version}-{flavor}.{ext}`; custom builds (with `--no-rename` or custom package) keep `app-{flavor}-{mode}.apk`.
- **Build mode matters**: debug builds produce `.zip` (Flutter's debug payload); release produces `.apk`. The tool handles this automatically.

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
