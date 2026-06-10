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
        _FILES=$(git -C "$_DOTS" diff --name-only HEAD origin/main 2>/dev/null)
        _DIRTY=$(git -C "$_DOTS" status --porcelain 2>/dev/null)
        if [ -n "$_DIRTY" ]; then
            printf "\033[33m[dotfiles] WARNING: local uncommitted changes — pull may fail:\033[0m\n"
            printf "\033[33m%s\033[0m\n" "$_DIRTY"
        fi
        if git -C "$_DOTS" pull --quiet origin main 2>/dev/null; then
            if echo "$_FILES" | grep -qE '^git/|bootstrap\.py'; then
                printf "\033[33m[dotfiles] structural change — re-run: python3 %s/bootstrap.py\033[0m\n" "$_DOTS"
            fi
            if echo "$_FILES" | grep -q 'settings\.json'; then
                printf "\033[33m[dotfiles] settings.json changed — restart Claude Code before using /model or /effort (stale sessions overwrite it)\033[0m\n"
            fi
            printf "\033[32m[dotfiles] synced\033[0m\n"
        else
            printf "\033[31m[dotfiles] PULL FAILED — resolve manually in %s\033[0m\n" "$_DOTS"
        fi
    fi
    echo "$_NOW" > "$_STAMP"
fi

unset _DOTS _STAMP _NOW _LAST _CHANGES _FILES _DIRTY
