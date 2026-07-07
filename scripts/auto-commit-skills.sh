#!/usr/bin/env bash
# ponytail: Stop-hook — auto-commit+push edits under claude/skills in the dotfiles repo.
# Runs every turn; fast-exits unless claude/skills changed. Cross-platform (bash: Git Bash on Win, bash on Mac).
# Best-effort push: on non-fast-forward, rebase (autostash) once and retry; if it still
# fails, leave the commit local and report. DRY_RUN=1 -> report only, no commit/push.
repo="$HOME/dotfiles"
scope="claude/skills"

[ -d "$repo/.git" ] || exit 0
[ -n "$(git -C "$repo" status --porcelain -- "$scope" 2>/dev/null)" ] || exit 0

git -C "$repo" add -- "$scope" 2>/dev/null
staged="$(git -C "$repo" diff --cached --name-only -- "$scope" 2>/dev/null)"
[ -n "$staged" ] || exit 0
count="$(printf '%s\n' "$staged" | grep -c .)"

if [ -n "$DRY_RUN" ]; then
  git -C "$repo" reset -q -- "$scope" 2>/dev/null   # leave the tree exactly as found
  printf 'DRY_RUN: would commit+push %s skill file(s)\n' "$count"
  exit 0
fi

git -C "$repo" commit -q -m "chore: auto-sync ${count} skill file(s)" 2>/dev/null || exit 0

push="pushed"
if ! git -C "$repo" push -q 2>/dev/null; then
  git -C "$repo" pull --rebase --autostash -q 2>/dev/null || true
  git -C "$repo" push -q 2>/dev/null || push="committed locally, push failed - resolve manually"
fi

printf '{"systemMessage":"skills auto-sync: %s file(s), %s","suppressOutput":true}\n' "$count" "$push"
exit 0
