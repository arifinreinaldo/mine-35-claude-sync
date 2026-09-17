# Swing Scanner

An independent swing/position scanner for US equities. It ranks structurally
strong names setting up for a move — using public methodologies (Weinstein
stage analysis, relative strength, volatility contraction, base breakouts) —
then filters them through your IPS phase and losers-pattern discipline.

It is **two halves**, by necessity:

```
  YOUR MACHINE                          COWORK
  ┌─────────────┐   swing_data.csv     ┌──────────────────┐
  │  fetch.py   │ ───────────────────► │  swing-scanner   │
  │ (Twelve Data)│   (you upload it)   │  skill (scan.py) │
  └─────────────┘                      └──────────────────┘
```

Why split: the Cowork sandbox is network-walled and FMP's free tier only
serves mega-caps. So the **data pull runs on your machine** (open network,
your API key) and the **analysis runs in the skill**. Your key never touches
the chat.

---

## Files

| File | Where it runs | What it does |
|---|---|---|
| `fetch.py` | Your machine | Pulls OHLCV from Twelve Data → `swing_data.csv` |
| `universe.txt` | Your machine | The ticker list `fetch.py` reads — edit freely |
| `SKILL.md` | Cowork | The skill definition |
| `scripts/scan.py` | Cowork (via skill) | Computes scores/setups/breadth from the CSV |

---

## One-time setup

1. **Python 3** on your machine (any recent version — `fetch.py` is pure
   standard library, no `pip install` needed).
2. **Get a free Twelve Data API key** at twelvedata.com (free tier: 800
   API calls/day, 8/min).
3. **Give `fetch.py` your key** — one of two ways (env var preferred):
   - **A — environment variable** (most secure):
     ```
     macOS / Linux:   export TWELVEDATA_API_KEY="your_key_here"
     Windows (cmd):   set TWELVEDATA_API_KEY=your_key_here
     ```
     Add the `export` line to `~/.zshrc` / `~/.bashrc` to make it permanent.
   - **B — a key file** named `env.text` next to `fetch.py`, one line:
     ```
     key=your_key_here
     ```
   Either way: never hardcode the key inside `fetch.py`, never paste it into
   a chat, and never commit `env.text` to git — add it to `.gitignore`. The
   env var wins if both are set.
4. Keep `fetch.py`, `universe.txt` (and `env.text` if you use option B) in
   the same folder.

---

## Running it

**On your machine:**
```
python3 fetch.py
```
It throttles to the free-tier limit (8 requests/min), so a ~150-ticker
universe takes roughly 18–20 minutes. It prints progress per ticker and
writes `swing_data.csv` when done. Failed tickers are listed and skipped.

Options:
```
python3 fetch.py --universe universe.txt --out swing_data.csv --days 400
python3 fetch.py --per-min 8        # throttle (raise only if you upgrade TD)
```

**Then, in Cowork:**
Upload `swing_data.csv` and ask the swing-scanner skill to run it — e.g.
*"run the swing scanner on this"* or *"scan these for setups."* It produces
a ranked watchlist with entry triggers, stops, and your phase/losers filter
already applied.

---

## Editing the universe

`universe.txt` is yours to curate — one ticker per line, `#` for comments.
Keep it ~150–300 names (the free tier comfortably covers that daily). Add
names you're tracking, remove what you don't care about. `SPY` and `RSP` are
added automatically as benchmarks — you don't need to list them.

A good universe = bottleneck/structural-theme leaders + sector leaders +
your current holdings + your watchlist. The seed list is a starting point,
not gospel.

---

## What it is — and isn't

- **Is:** a curated-universe, EOD, relative-strength + setup ranker with a
  built-in discipline layer (IPS phase gating, losers-pattern exclusion,
  mechanical stops on every setup).
- **Isn't:** a whole-market scanner, an intraday/live tool, a fundamentals
  engine, or financial advice. It surfaces *candidates*; the thesis decides
  if you act. Pair it with deeper research before any real buy.
