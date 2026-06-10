# mine-35-claude-sync

Personal dotfiles — Claude Code config, skills, and git settings synced across Windows, Mac, and Linux.

---

## Bootstrap a new machine

### In a Claude Code terminal (any OS)

Just tell Claude:

> Clone https://github.com/arifinreinaldo/mine-35-claude-sync.git and run bootstrap.py

Claude will detect your OS and handle everything automatically.

---

### Manual — Windows

> **Requires:** Developer Mode — Settings → System → For Developers → Developer Mode

```powershell
git clone https://github.com/arifinreinaldo/mine-35-claude-sync.git "$env:USERPROFILE\dotfiles"
python "$env:USERPROFILE\dotfiles\bootstrap.py"
```

### Manual — Mac / Linux

```bash
git clone https://github.com/arifinreinaldo/mine-35-claude-sync.git ~/dotfiles
python3 ~/dotfiles/bootstrap.py
```

The bootstrap script will:
- Auto-detect your OS
- Symlink all configs to their correct locations
- Install the auto-sync hook into your shell profile
- Back up any existing files as `.bak` before overwriting

---

## What gets synced

| File / Folder | Location |
|---|---|
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `claude/settings.json` | `~/.claude/settings.json` |
| `claude/skills/` | `~/.claude/skills/` |
| `git/gitconfig.windows` · `git/gitconfig.macos` · `git/gitconfig.linux`† | `~/.gitconfig` |

---

## How sync works

Every terminal open, the shell checks if 3 hours have passed since the last sync. If yes, it runs `git fetch` to check for changes. If changes exist, it pulls immediately and announces the update. If nothing is new, it silently resets the timer.

Push from any machine → all other machines pick it up within 3 hours on next terminal open.

To force a sync right now, use the Claude Code skill:

```
/sync-dotfiles
```

---

## Windows: re-bootstrap after the gitconfig rename (one-time)

**For Claude / anyone working on the Windows machine:** the OS-aware change renamed `git/.gitconfig` → `git/gitconfig.windows`. If this machine was bootstrapped **before** that change, `~/.gitconfig` is now a **dangling symlink** (it points at the deleted old path), so Git has no global `user.name` / `user.email`.

Fix — run once, after the repo has pulled the change:

```powershell
python "$env:USERPROFILE\dotfiles\bootstrap.py"
```

This repoints `~/.gitconfig` → `git/gitconfig.windows` (`arifinreinaldo` / `arifin.reinaldo+windows@gmail.com`). Verify:

```powershell
git config user.email   # should print ...+windows@gmail.com
```

> The auto-sync hook only runs `git pull` — it **never re-creates symlinks**. Any structural change (a renamed or newly added synced file) needs `bootstrap.py` re-run on machines that were already set up.

---

## Adding something new

1. Drop the file into the repo under the right folder (`claude/`, `git/`, etc.)
2. Add a `symlink()` line to `bootstrap.py`
3. Commit and push — all devices pick it up within 3 hours

---

## Notes

- `.gitconfig` is **OS-specific**: bootstrap symlinks `git/gitconfig.windows` (Windows), `git/gitconfig.macos` (macOS), or `git/gitconfig.linux` (Linux), and **skips it entirely if no variant exists** for the current OS. † `gitconfig.linux` isn't committed yet — Linux machines skip the symlink (keeping their own `~/.gitconfig`) until you add one.
- Git identity is shared (`name = arifinreinaldo`) but **email is OS-tagged** — `arifin.reinaldo+windows@gmail.com`, `arifin.reinaldo+macos@gmail.com`, etc. — so you can tell which machine authored a commit. Keep other per-OS settings (line endings, GUI tool paths, credential helpers) in the matching variant; never share one `.gitconfig` across OSes.
- `~/.claude/settings.local.json` is intentionally excluded — it holds machine-specific permissions.
- `~/.claude/memory/` is excluded — it's path-encoded per machine.
