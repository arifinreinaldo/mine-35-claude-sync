#!/usr/bin/env bash
# Bootstrap script for Mac/Linux
# Usage: bash setup.sh

set -e

DOTFILES="$HOME/dotfiles"
REPO="https://github.com/arifinreinaldo/mine-35-claude-sync.git"

# Clone if not already present
if [ ! -d "$DOTFILES" ]; then
    git clone "$REPO" "$DOTFILES"
fi

link() {
    local path="$1"
    local target="$2"
    local dir
    dir="$(dirname "$path")"

    mkdir -p "$dir"

    if [ -L "$path" ]; then
        echo "SKIP (already linked): $path"
        return
    fi

    if [ -e "$path" ]; then
        echo "BACKUP: $path -> $path.bak"
        mv "$path" "$path.bak"
    fi

    ln -sf "$target" "$path"
    echo "LINKED: $path -> $target"
}

# Claude Code
link "$HOME/.claude/CLAUDE.md"     "$DOTFILES/claude/CLAUDE.md"
link "$HOME/.claude/settings.json" "$DOTFILES/claude/settings.json"
link "$HOME/.claude/skills"        "$DOTFILES/claude/skills"

# Git — gitconfig is OS-specific; use the unix variant on macOS/Linux
if [ -f "$DOTFILES/git/gitconfig.unix" ]; then
    link "$HOME/.gitconfig" "$DOTFILES/git/gitconfig.unix"
else
    echo "SKIP: no git/gitconfig.unix in repo"
fi

# Shell hook — add daily sync to .zshrc or .bashrc
HOOK=". \"$DOTFILES/scripts/sync.sh\""
SHELL_RC="$HOME/.zshrc"
[ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.bashrc"

if [ -f "$SHELL_RC" ] && grep -q "dotfiles/scripts/sync" "$SHELL_RC" 2>/dev/null; then
    echo "SKIP (already hooked): $SHELL_RC"
else
    printf "\n# Dotfiles auto-sync\n%s\n" "$HOOK" >> "$SHELL_RC"
    echo "HOOK: added sync to $SHELL_RC"
fi

echo ""
echo "Done. All dotfiles linked and shell hook installed."
