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

def sh(cmd, **kw):
    subprocess.run(cmd, shell=True, check=True, **kw)

def ps(cmd):
    subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True)

def symlink(src: Path, dst: Path):
    if dst.is_symlink():
        print(f"  SKIP   {dst}")
        return
    if dst.exists():
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
    sh(f'git clone "{REPO}" "{DOTS}"')
else:
    print(f"[bootstrap] repo exists, pulling latest...")
    sh(f'git -C "{DOTS}" pull --quiet origin main')

# ── Symlinks ──────────────────────────────────────────────────────────────────

print("\n[bootstrap] creating symlinks...")
CLAUDE = HOME / ".claude"
CLAUDE.mkdir(exist_ok=True)

symlink(DOTS / "claude" / "CLAUDE.md",     CLAUDE / "CLAUDE.md")
symlink(DOTS / "claude" / "settings.json", CLAUDE / "settings.json")
symlink(DOTS / "claude" / "skills",        CLAUDE / "skills")
symlink(DOTS / "git"    / ".gitconfig",    HOME   / ".gitconfig")

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
