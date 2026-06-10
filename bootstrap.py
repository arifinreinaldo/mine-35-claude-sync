#!/usr/bin/env python3
"""
Dotfiles bootstrap — auto-detects OS, creates symlinks, installs shell hook.
Usage: python3 bootstrap.py
"""
import os
import platform
import subprocess
import sys
from pathlib import Path

REPO  = "https://github.com/arifinreinaldo/mine-35-claude-sync.git"
HOME  = Path.home()
DOTS  = HOME / "dotfiles"

# ── OS detection ─────────────────────────────────────────────────────────────

system = platform.system()
IS_WIN = system == "Windows"
IS_MAC = system == "Darwin"
IS_LNX = system == "Linux"

print(f"[bootstrap] OS: {system}")

# ── Helpers ───────────────────────────────────────────────────────────────────

# git must work even when ~/.gitconfig is a dangling symlink — that's one of
# the things bootstrap repairs. Ignore the global config for our own git calls.
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull}

def git(cmd):
    subprocess.run(cmd, shell=True, check=True, env=GIT_ENV)

def ps(cmd):
    subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True)

def _remove_link(p: Path):
    try:
        p.unlink()
    except (IsADirectoryError, PermissionError):
        p.rmdir()  # Windows directory symlink needs rmdir

def symlink(src: Path, dst: Path):
    if dst.is_symlink():
        try:
            if dst.resolve(strict=True) == src.resolve():
                print(f"  SKIP   {dst}")
                return
        except OSError:
            pass  # dangling — target was deleted/renamed
        print(f"  REPAIR {dst} (stale link)")
        _remove_link(dst)
    elif dst.exists():
        bak = dst.with_suffix(dst.suffix + ".bak")
        print(f"  BACKUP {dst} → {bak}")
        dst.rename(bak)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if IS_WIN:
        ps(f'New-Item -ItemType SymbolicLink -Path "{dst}" -Target "{src}"')
    else:
        dst.symlink_to(src)
    print(f"  LINK   {dst} → {src}")

def add_hook(rc: Path, marker: str, hook: str):
    content = rc.read_text(errors="replace") if rc.exists() else ""
    if marker in content:
        print(f"  SKIP   hook already in {rc}")
        return
    rc.parent.mkdir(parents=True, exist_ok=True)
    with rc.open("a") as f:
        f.write(f"\n# Dotfiles auto-sync\n{hook}\n")
    print(f"  HOOK   {rc}")

# ── Clone ─────────────────────────────────────────────────────────────────────

if not DOTS.exists():
    print(f"[bootstrap] cloning repo...")
    git(f'git clone "{REPO}" "{DOTS}"')
else:
    print(f"[bootstrap] repo exists, pulling latest...")
    git(f'git -C "{DOTS}" pull --quiet origin main')

# ── Symlinks ──────────────────────────────────────────────────────────────────

print("\n[bootstrap] creating symlinks...")
CLAUDE = HOME / ".claude"
CLAUDE.mkdir(exist_ok=True)

symlink(DOTS / "claude" / "CLAUDE.md",     CLAUDE / "CLAUDE.md")
symlink(DOTS / "claude" / "settings.json", CLAUDE / "settings.json")
symlink(DOTS / "claude" / "skills",        CLAUDE / "skills")

# gitconfig is OS-specific — pick the matching variant, skip if absent
_gitcfg_name = "gitconfig.windows" if IS_WIN else "gitconfig.macos" if IS_MAC else "gitconfig.linux"
gitconfig = DOTS / "git" / _gitcfg_name
if gitconfig.exists():
    symlink(gitconfig, HOME / ".gitconfig")
else:
    print(f"  SKIP   no gitconfig for this OS ({gitconfig.name} not in repo)")

# ── Shell hook ────────────────────────────────────────────────────────────────

print("\n[bootstrap] installing shell hook...")

if IS_WIN:
    result = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", "echo $PROFILE"],
        text=True
    ).strip()
    profile = Path(result)
    hook    = f'. "{DOTS}\\scripts\\sync.ps1"'
    add_hook(profile, r"dotfiles\scripts\sync", hook)

elif IS_MAC:
    # macOS default shell is zsh since Catalina
    zshrc = HOME / ".zshrc"
    hook  = f'. "{DOTS}/scripts/sync.sh"'
    add_hook(zshrc, "dotfiles/scripts/sync", hook)

else:  # Linux — prefer zsh, fallback to bash
    rc   = HOME / ".zshrc" if (HOME / ".zshrc").exists() else HOME / ".bashrc"
    hook = f'. "{DOTS}/scripts/sync.sh"'
    add_hook(rc, "dotfiles/scripts/sync", hook)

# ── Done ──────────────────────────────────────────────────────────────────────

print("\n[bootstrap] done. open a new terminal — configs are live.\n")
