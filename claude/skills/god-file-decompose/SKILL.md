---
name: god-file-decompose
description: Decide whether a god file or god method is safe to decompose in one shot, and produce the slice plan if it is not. Use when the user asks to split, decompose, break up, refactor, or "clean up" a large file, class, or method, or asks whether such a refactor is safe.
---

# God File Decomposition

Answer the safety question with measurements, not opinion. Then give a slice plan.

## Rule

Never start extracting before the measurement runs. A god file that looks
mechanical almost never is; the hazards are invisible in a skim.

Default verdict is **not safe one-shot**. Move off that default only when
every gate below passes.

## Step 1 — Measure

Run these against the target. Record the numbers; they are the answer.

```bash
F=path/to/target.dart          # or .kt, .php, .py, .go
wc -l "$F"
grep -nE "^(class|mixin|extension|enum|abstract) " "$F"     # class count
```

Find the biggest member, then slice it into a temp file and measure the body:

```bash
awk 'NR>=START && NR<=END' "$F" > /tmp/body.txt
echo "return  : $(grep -cE '^\s+return ' /tmp/body.txt)"
echo "continue: $(grep -cE '\bcontinue\b'  /tmp/body.txt)"
echo "break   : $(grep -cE '\bbreak\b'     /tmp/body.txt)"
echo "await   : $(grep -cE '\bawait\b'     /tmp/body.txt)"
echo "try     : $(grep -cE '^\s+try *\{'   /tmp/body.txt)"
```

Then the test net and the churn:

```bash
grep -rl "$(basename "$F" .dart)" test/ | xargs wc -l
git log --since="6 months ago" --oneline -- "$F" | wc -l
```

## Step 2 — The five gates

Report each gate as PASS or FAIL with its number. Any FAIL means not
safe one-shot.

| Gate | FAIL when |
|---|---|
| **Non-local control flow** | The god method holds a loop, and branches inside it use `continue` / `break` / early `return`. Count them. Each one is loop semantics that cannot move into an extracted function; it must become a signal value the caller re-interprets. |
| **Shadowing** | An instance field and a local or parameter share a name, and the code never qualifies with `this.` / `self.` / `$this->`. Extraction rebinds the identifier silently. The compiler stays quiet. |
| **Characterization tests** | Test lines are under ~10% of source lines, or no test exercises the god method's branches. Without a net, a wrong extraction ships. |
| **Churn** | The file changes more than ~2x/month. A big-bang rewrite guarantees merge conflicts against work already in flight. |
| **Shared mutable state** | Locals declared before the branch chain get written by one branch and read by a later one. Extraction must thread them through parameters and back. |

## Step 3 — Verify the shadowing gate by hand

Grep is not enough. For each field name that also appears as a local or a
parameter, confirm whether the body reassigns the local:

```bash
grep -nE "^\s+(name1|name2) *=" /tmp/body.txt      # reassignment sites
grep -cE "this\.(name1|name2)"   /tmp/body.txt      # qualified uses
```

A reassignment plus zero qualified uses is the worst case. The local and the
field hold different values, and extraction picks the wrong one.

## Step 4 — Output

Lead with the verdict in one line. Then the measurement table. Then at most
three named killers with `file:line` citations. Then the slice plan.

Never hand back a decomposition plan alone. The user asked whether it is safe.

## The slice plan

Order the work so each commit is independently revertible and provable.

1. **De-risk first.** Rename shadowed parameters. Mechanical, compiler-verified,
   touches no logic. This one IS safe one-shot, and it removes the silent
   failure mode from every later step.
2. **Characterize what you will touch.** Write tests for the branch families
   you actually plan to change. Not all of them. Coverage you never use is
   waste.
3. **Extract one family per commit.** Branches with no `continue` / `break` /
   `return` go first; those are the genuinely mechanical ones. Branches with
   non-local jumps go last, one at a time, each with its own test.
4. **Stop when the pain stops.** A god file nobody opens costs nothing.
   Decompose the parts that block edits, leave the rest.

## Anti-patterns

- Extracting a branch body that contains `continue` and turning it into a
  plain `void` helper. The loop now runs the code that the `continue` skipped.
- Converting an `if/else if` chain to a dispatch map in one commit. The map
  loses fall-through order and the non-local jumps at the same time.
- "The analyzer passes" as proof. Both the shadowing failure and the
  control-flow failure compile clean.
- Running the whole decomposition on a branch that also carries feature work.
  Keep the refactor alone so a revert stays cheap.

## When one-shot IS safe

All five gates pass, and the god file is a flat collection of independent
members with no shared loop, no shared mutable locals, and no shadowing.
Split by moving whole members, change nothing inside them, and prove it with
the build plus a diff that shows only moves.
