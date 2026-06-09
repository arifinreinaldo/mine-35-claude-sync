# mine-35-claude-sync

Personal dotfiles — Claude Code config, skills, and git settings synced across Windows, Mac, and Linux.

---

## Bootstrap a new machine

### Windows

> **Requires:** Developer Mode enabled — Settings → System → For Developers → Developer Mode

Open PowerShell and run:

```powershell
git clone https://github.com/arifinreinaldo/mine-35-claude-sync.git "$env:USERPROFILE\dotfiles"
& "$env:USERPROFILE\dotfiles\setup.ps1"
```

### Mac / Linux

```bash
git clone https://github.com/arifinreinaldo/mine-35-claude-sync.git ~/dotfiles && bash ~/dotfiles/setup.sh
```

That's it. The script will:
- Symlink all configs to their correct locations
- Install a daily auto-sync hook into your shell profile
- Back up any existing files as `.bak` before overwriting

---

## What gets synced

| File / Folder | Location |
|---|---|
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `claude/settings.json` | `~/.claude/settings.json` |
| `claude/skills/` | `~/.claude/skills/` |
| `git/.gitconfig` | `~/.gitconfig` |

---

## How sync works

On the **first terminal open each day**, the shell automatically runs `git pull` on this repo. All symlinked files update instantly — no manual steps.

To manually sync at any time, use the Claude Code skill:

```
/sync-dotfiles
```

---

## Adding something new

1. Drop the file into the repo under the right folder (`claude/`, `git/`, etc.)
2. Add a symlink line to both `setup.ps1` and `setup.sh`
3. Commit and push — all devices pick it up on next terminal open

---

## Notes

- `core.autocrlf = true` in `.gitconfig` is Windows-specific. On Mac/Linux, change to `autocrlf = input` after setup if needed.
- `~/.claude/settings.local.json` is intentionally excluded — it holds machine-specific permissions.
- `~/.claude/memory/` is excluded — it's path-encoded per machine.
