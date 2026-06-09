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

# Git
# NOTE: autocrlf=true in .gitconfig is Windows-specific.
# On Mac/Linux you may want to change it to: autocrlf=input
link "$HOME/.gitconfig" "$DOTFILES/git/.gitconfig"

echo ""
echo "Done. All dotfiles linked."
