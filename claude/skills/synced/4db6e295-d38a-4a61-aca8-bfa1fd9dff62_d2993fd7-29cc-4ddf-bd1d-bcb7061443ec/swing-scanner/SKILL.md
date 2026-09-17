---
name: swing-scanner
description: "Independent swing/position scanner for Yu. Ingests a swing_data.csv (produced on Yu's own machine by the bundled fetch.py, which pulls Twelve Data) and ranks US equities for high-relative-strength structural setups using public methodologies — Weinstein stage analysis, relative strength, volatility contraction, base breakouts. Use whenever Yu uploads a swing_data.csv or asks to scan for setups, find swing candidates, check relative strength, run the scanner, build a watchlist, or asks 'what looks strong', 'any setups', 'screen for me'. Applies Yu's IPS phase, losers-pattern exclusion, and buyer-not-trader discipline before any name reaches the output. No paid screener, no scraping — Yu's API key never leaves his machine."
---

# Swing Scanner

A curated-universe scanner that ranks **structurally strong US equities setting up for a move**, then filters them through Yu's discipline before anything reaches the watchlist.

## Architecture — two halves, by necessity

The Cowork sandbox is network-walled (allowlist proxy) and FMP's free tier only serves a mega-cap whitelist — so the scanner is split:

1. **`fetch.py` runs on Yu's own machine.** It reads `universe.txt`, pulls ~14 months of daily OHLCV from Twelve Data (Yu's free API key, set as an env var — never pasted into chat), and writes one flat **`swing_data.csv`**. See `README.md` for run instructions.
2. **This skill runs in Cowork.** Yu uploads `swing_data.csv`; the skill runs the bundled `scripts/scan.py` on it, applies the Yu-filter, and outputs the ranked watchlist.

The key never touches this chat; the data problem is solved on Yu's machine; the judgment layer lives here.

## Why this exists

Yu's portfolio analyzer is a strong *risk* engine but has no *opportunity* engine — it only audits what he already owns. This is the opportunity layer. It is deliberately **not** a day-trading tool: the methodologies (Weinstein stages, relative strength, volatility contraction, base breakouts) are public, book-derived techniques that reward *buyers* — entering structurally strong names on constructive setups and holding. That matches Yu's winners (gold, NVO, structural compounders bought DCA-early) and avoids his losers (late-cycle FOMO on hyped, parabolic, no-base names).

The single most important thing this skill does: pair every candidate with a **mechanical falsification level** — a pre-defined "I'm wrong if price hits X." That exit discipline separates a survivable upside engine from −70% bag-holds.

## Yu context (applied automatically)

- **IPS phases:** Phase 1 (wedding prep → Jan 2027) = *preserve* — scanner runs **watchlist-only**, emits NO buy calls. Phase 2 (wife arriving) / Phase 3 (steady state) = ranked buy candidates with sizing. **Default to Phase 1** unless told otherwise.
- **Buyer, not trader:** base/pullback entries on quality, never chasing. No shorts, no intraday.
- **Losers pattern:** parabolic / extended / no-base names are Yu's documented failure mode — flagged and *excluded* from buy ranks.
- **Currency:** US (USD bucket) scanner. Note USD-bucket IPS gates in output.

## Workflow

### Step 1 — Get the data file
Yu uploads `swing_data.csv` (produced by `fetch.py` on his machine). If he hasn't run `fetch.py` yet, point him to `README.md`. If the upload is missing/empty, stop and ask — never fabricate prices.

### Step 2 — Compute (bundled script, not prose-math)
Run `python3 scripts/scan.py --csv <uploaded swing_data.csv> --out results.json`. The script does ALL deterministic computation — see "Scoring model". Do not re-derive any of it by reasoning.

### Step 3 — Apply the Yu-filter
On `results.json`:
1. **Phase gate** — Phase 1 ⇒ everything is `WATCH`, no buy tier. Phase 2/3 ⇒ buy tiers allowed.
2. **Losers-pattern exclusion** — any name flagged `PARABOLIC` or `NO_BASE` is moved out of buy ranks into the "Ignore / wait for pullback" list, with the run % shown.
3. **Holdings cross-ref** — tag names Yu already owns (from the latest Tracker if available) so the scan doubles as an add-on-strength check.

### Step 4 — Output
Emit the ranked Markdown watchlist (see "Output format"). Lead with the breadth/regime read — it decides whether *any* setup is worth acting on.

## Scoring model (what `scan.py` computes)

Per ticker, from daily OHLCV:

- **Trend stage** (Weinstein): price vs 150-day MA + that MA's slope → Stage 1 (basing) / 2 (advancing — the only buyable stage) / 3 (topping) / 4 (declining).
- **MA alignment:** 10/20/50/200-day SMAs; `aligned` when 10>20>50>200 and price above all.
- **Relative Strength vs SPY:** ratio line; RS percentile across the universe (0–99); `rs_new_high` flag. *Dominant factor — strong names lead, weak names bag-hold.*
- **Momentum:** 1/3/6-month return.
- **Volatility contraction (VCP-ish):** progressively tighter pullbacks on declining volume → score 0–3.
- **Distance from 52-week high.**
- **Volume signature:** up-day vs down-day volume over 50 days → accumulation vs distribution.
- **Composite Swing Score (0–100):** RS percentile 35% · trend stage 25% · MA alignment 15% · volume signature 15% · volatility contraction 10%. Weights documented in `scan.py` — transparent and tunable.
- **Risk flags:** `PARABOLIC` (>60% in 90d), `NO_BASE` (>40% in 90d, no consolidation), `EXTENDED` (>20% above 50-day MA), `STAGE_4`.

Universe-level: **breadth** — % above 50-day / 200-day MA; SPY vs RSP (narrow vs broad leadership); `weak_breadth_warning`.

## The setups (pre-defined — `scan.py` flags these)

Three, all public, all buyer-appropriate. Each MUST carry an entry trigger AND a stop — a setup with no stop is not a setup.

1. **Tight near highs** — Stage 2, within 15% of 52w high, contraction ≥ 2. *Entry:* break of consolidation high. *Stop:* below the contraction low.
2. **Pullback to rising 50-day** — Stage 2, within ~3% of a rising 50-day MA on light volume. *Entry:* reclaim/hold the 50-day. *Stop:* decisive close below it.
3. **Base breakout** — emerging from a Stage 1 base (≥5 weeks, <25% deep), RS line turning up. *Entry:* break of the base. *Stop:* back into the base.

## Yu-filter rules

- **Phase 1 (default):** tier is `WATCH` only. Still rank and show everything — Yu *builds the watchlist now*, just doesn't deploy (preserve mode).
- **Phase 2/3:** `T1 STRONG` (score ≥ 80, setup present, no risk flags) · `T2 ADD` (65–79) · `WATCH` (rest).
- **Losers-pattern exclusion:** `PARABOLIC` or `NO_BASE` ⇒ never a buy tier, regardless of score. Goes to "Ignore / wait for pullback" with run % and a `-15% pullback` re-entry note.
- **Breadth gate:** universe breadth < 40% above 50-day MA ⇒ header warning, downgrade tone from "act" to "watch only" even in Phase 2/3.
- **Sizing (Phase 2/3 only):** never more than ~0.5–1% of book per entry, DCA pace, never lump sum.

## Output format

Markdown, always this order:

```
# Swing Scan — <as_of date from CSV>

## Tape
<breadth %, SPY vs RSP leadership, 1-line regime read>
<if weak_breadth_warning: explicit "poor breadth — setups unreliable" line>

## Ranked Watchlist
| Rank | Ticker | Score | Stage | RS%ile | Setup | Entry Trigger | Stop | Holding? | Tier |
...top 15-20...

## Ignore / wait for pullback
<names excluded by the losers-pattern filter, with run % and re-entry note>

## Notes
- Phase: <1/2/3> — <what tier output means in this phase>
- Universe size, data as_of date
- EOD data, curated universe, US only. Not whole-market, not intraday, not advice.
```

End every run with: *"Informational scan, not financial advice. EOD data, curated universe."*

## Honest limitations (state these; don't hide them)

- **Curated universe, not whole-market** — it sees what's in `universe.txt`. A great setup outside the list is invisible. Deliberate tradeoff for a free, self-owned tool.
- **EOD data** — entry triggers are next-day decisions, not live alerts.
- **US only** — no usable free IDX/SGX history.
- **Data is only as fresh as the last `fetch.py` run** — the CSV carries an as_of date; surface it.
- **No fundamentals** — technical/relative-strength only. Pair with `equity-research:thesis` before any real buy: strength gets you the candidate, the thesis decides if you act.
- **The score is a ranking, not a prediction.**
