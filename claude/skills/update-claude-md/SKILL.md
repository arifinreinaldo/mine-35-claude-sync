---
name: update-claude-md
description: Safely push CLAUDE.md updates — pull latest first, detect overlap, merge intelligently before committing
---

Use this skill whenever the user wants to update or push changes to their CLAUDE.md.

## Step 1 — Fetch remote state

Run these two commands:

```
git -C ~/dotfiles fetch origin main
git -C ~/dotfiles log HEAD..origin/main --oneline -- claude/CLAUDE.md
```

Windows path: replace `~/dotfiles` with `$env:USERPROFILE\dotfiles`.

- If output is **empty**: remote has no new changes to CLAUDE.md. Skip to Step 4.
- If output has **commits**: remote has changes. Continue to Step 2.

## Step 2 — Show both versions side by side

Read both versions:

- **Local (current):** Read `~/dotfiles/claude/CLAUDE.md`
- **Remote:** Run `git -C ~/dotfiles show origin/main:claude/CLAUDE.md`

Then diff them:

```
git -C ~/dotfiles diff HEAD origin/main -- claude/CLAUDE.md
```

## Step 3 — Merge intelligently

Analyze the two versions section by section. For each section:

| Situation | Action |
|---|---|
| Identical in both | Keep once, no change needed |
| Only in local | Keep — it's new work from this machine |
| Only in remote | Keep — it's new work from another machine |
| Both have it but differ | **Highlight the conflict**, show both variants, ask the user which to keep or how to combine |
| Contradictory instructions | Flag explicitly — do not silently pick one |

Write the merged CLAUDE.md. Show a brief summary:
- N sections kept from local
- N sections kept from remote  
- N conflicts resolved (list them)
- N conflicts requiring user input (list them and pause)

Do not proceed past a conflict that needs user input. Wait for confirmation.

## Step 4 — Pull remote changes

Once the merge is ready (or if there were no remote changes):

```
git -C ~/dotfiles pull origin main
```

If there is a git merge conflict (CONFLICT markers in the file), resolve it using the merged content from Step 3.

## Step 5 — Commit and push

```
git -C ~/dotfiles add claude/CLAUDE.md
git -C ~/dotfiles commit -m "chore: update CLAUDE.md"
git -C ~/dotfiles push origin main
```

Use a more descriptive commit message if the user described what they changed.

## Rules

- Never push without pulling first.
- Never silently discard content from either version.
- Never combine two contradictory instructions — always surface the conflict to the user.
- Keep the merged file clean: no duplicate sections, no merge markers.

---

## Self-Improvement Protocol

When a blocker interrupts this skill — a step that fails, a missing precondition, or a wrong/ambiguous instruction above — before moving on:

1. **Document** — add a bullet under **Known Blockers**: what you tried, what happened, and the root cause (not just the symptom).
2. **Solve & verify** — apply a fix and confirm it actually works (evidence, not assertion).
3. **Self-improve** — once verified, add a dated line to **Changelog**, then rewrite the affected instruction(s) above so the fix is baked in and the blocker can't recur. Memorialize only reproducible, structural blockers — not one-off transient failures.
4. **Escalate if risky** — if the rewrite is uncertain, high-blast-radius, or changes this skill's core behavior, do NOT self-edit: show the user the proposed change and get review first.

### Known Blockers

_None yet._

### Changelog

<!-- YYYY-MM-DD — blocker → fix -->
