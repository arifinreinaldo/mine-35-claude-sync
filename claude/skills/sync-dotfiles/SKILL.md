---
name: sync-dotfiles
description: Sync dotfiles repo — pull latest from origin and report what changed
---

When this skill is invoked, do the following:

1. Run `git -C ~/dotfiles fetch origin main` to check for remote changes.
2. Run `git -C ~/dotfiles log HEAD..origin/main --oneline` to show what's incoming.
3. If there are changes, run `git -C ~/dotfiles pull origin main` and report what was updated.
4. If already up to date, say so in one line.
5. Update `.last-sync` with today's date so the shell hook skips the auto-pull today:
   - Windows: `(Get-Date).ToString("yyyy-MM-dd") | Set-Content "$env:USERPROFILE\dotfiles\.last-sync"`
   - Mac/Linux: `date +%Y-%m-%d > ~/dotfiles/.last-sync`

Keep the output short. Show file changes if any, otherwise "already up to date."
