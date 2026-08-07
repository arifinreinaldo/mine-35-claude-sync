#!/usr/bin/env bash
# ponytail: Stop-hook — auto-commit+push edits under claude/skills and claude/settings.json.
# settings.json carries enabledPlugins + extraKnownMarketplaces, which restore the plugin set
# on a new machine. CLAUDE.md stays out of scope on purpose: /update-claude-md owns that file.
# Runs every turn; fast-exits unless the scope changed. Cross-platform (bash: Git Bash on Win, bash on Mac).
# Best-effort push: on non-fast-forward, rebase (autostash) once and retry; if it still
# fails, leave the commit local and report. DRY_RUN=1 -> report only, no commit/push.
repo="$HOME/dotfiles"
scope=(claude/skills claude/settings.json)

[ -d "$repo/.git" ] || exit 0
[ -n "$(git -C "$repo" status --porcelain -- "${scope[@]}" 2>/dev/null)" ] || exit 0

git -C "$repo" add -- "${scope[@]}" 2>/dev/null
staged="$(git -C "$repo" diff --cached --name-only -- "${scope[@]}" 2>/dev/null)"
[ -n "$staged" ] || exit 0
count="$(printf '%s\n' "$staged" | grep -c .)"

if [ -n "$DRY_RUN" ]; then
  git -C "$repo" reset -q -- "${scope[@]}" 2>/dev/null   # leave the tree exactly as found
  printf 'DRY_RUN: would commit+push %s claude file(s)\n' "$count"
  exit 0
fi

git -C "$repo" commit -q -m "chore: auto-sync ${count} claude config file(s)" 2>/dev/null || exit 0

push="pushed"
if ! git -C "$repo" push -q 2>/dev/null; then
  git -C "$repo" pull --rebase --autostash -q 2>/dev/null || true
  git -C "$repo" push -q 2>/dev/null || push="committed locally, push failed - resolve manually"
fi

printf '{"systemMessage":"skills auto-sync: %s file(s), %s","suppressOutput":true}\n' "$count" "$push"
exit 0
