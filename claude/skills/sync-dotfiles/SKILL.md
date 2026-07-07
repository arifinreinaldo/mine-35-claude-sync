---
name: sync-dotfiles
description: Sync dotfiles repo — pull latest from origin and report what changed. Triggers on "sync dotfiles", "sync claude root", "sync claude.md", "update claude config/root", "pull claude config" — the claude/ subtree (CLAUDE.md, settings.json, skills/) is symlinked from this repo.
---

When this skill is invoked, do the following:

1. Run `git -C ~/dotfiles fetch origin main` to check for remote changes.
2. Run `git -C ~/dotfiles log HEAD..origin/main --oneline` to show what's incoming.
3. If there are changes, run `git -C ~/dotfiles pull origin main` and report what was updated.
4. If already up to date, say so in one line.
5. Update `.last-sync` with the current Unix epoch (in **seconds**) so the shell hook skips the auto-pull until the next interval. The `sync.ps1` hook reads this value with `[long]` — it MUST be an integer epoch, not a date string:
   - Windows: `[DateTimeOffset]::UtcNow.ToUnixTimeSeconds() | Set-Content "$env:USERPROFILE\dotfiles\.last-sync"`
   - Mac/Linux: `date +%s > ~/dotfiles/.last-sync`

Keep the output short. Show file changes if any, otherwise "already up to date."

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
