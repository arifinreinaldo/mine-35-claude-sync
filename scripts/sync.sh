#!/usr/bin/env bash
# Dotfiles sync — source from .zshrc / .bashrc
# Checks every 3 hours; fetches first, only pulls when changes exist
_DOTS="$HOME/dotfiles"
_STAMP="$_DOTS/.last-sync"
_NOW=$(date +%s)
_LAST=$(cat "$_STAMP" 2>/dev/null || echo 0)

if [ $((_NOW - _LAST)) -ge 10800 ]; then
    git -C "$_DOTS" fetch --quiet origin main 2>/dev/null
    _CHANGES=$(git -C "$_DOTS" log HEAD..origin/main --oneline 2>/dev/null)
    if [ -n "$_CHANGES" ]; then
        printf "\033[36m[dotfiles] update found, syncing...\033[0m\n"
        git -C "$_DOTS" pull --quiet origin main 2>/dev/null
        printf "\033[32m[dotfiles] synced\033[0m\n"
    fi
    echo "$_NOW" > "$_STAMP"
fi

unset _DOTS _STAMP _NOW _LAST _CHANGES
