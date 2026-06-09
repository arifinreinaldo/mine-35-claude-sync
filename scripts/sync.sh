#!/usr/bin/env bash
# Dotfiles daily sync — source from .zshrc / .bashrc
_DOTFILES="$HOME/dotfiles"
_STAMP="$_DOTFILES/.last-sync"
_TODAY=$(date +%Y-%m-%d)

if [ ! -f "$_STAMP" ] || [ "$(cat "$_STAMP" 2>/dev/null)" != "$_TODAY" ]; then
    printf "\033[36m[dotfiles] syncing...\033[0m\n"
    if git -C "$_DOTFILES" pull --quiet origin main 2>/dev/null; then
        echo "$_TODAY" > "$_STAMP"
        printf "\033[32m[dotfiles] synced\033[0m\n"
    else
        printf "\033[33m[dotfiles] sync failed (offline?)\033[0m\n"
    fi
fi

unset _DOTFILES _STAMP _TODAY
