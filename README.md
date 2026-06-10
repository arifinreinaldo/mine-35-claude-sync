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
| `git/gitconfig.windows` *(Windows)* · `git/gitconfig.unix` *(macOS/Linux)* | `~/.gitconfig` |

---

## How sync works

Every terminal open, the shell checks if 3 hours have passed since the last sync. If yes, it runs `git fetch` to check for changes. If changes exist, it pulls immediately and announces the update. If nothing is new, it silently resets the timer.

Push from any machine → all other machines pick it up within 3 hours on next terminal open.

To force a sync right now, use the Claude Code skill:

```
/sync-dotfiles
```

---

## Adding something new

1. Drop the file into the repo under the right folder (`claude/`, `git/`, etc.)
2. Add a `symlink()` line to `bootstrap.py`
3. Commit and push — all devices pick it up within 3 hours

---

## Notes

- `.gitconfig` is **OS-specific**: bootstrap symlinks `git/gitconfig.windows` on Windows and `git/gitconfig.unix` on macOS/Linux, and **skips it entirely if no variant exists** for the current OS. Keep per-OS settings (line endings, GUI tool paths, credential helpers, identity) in the matching variant — never share one `.gitconfig` across OSes.
- `~/.claude/settings.local.json` is intentionally excluded — it holds machine-specific permissions.
- `~/.claude/memory/` is excluded — it's path-encoded per machine.
