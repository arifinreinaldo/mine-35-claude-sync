---
name: pre-pop-scanner
description: Weekly scan to find small-cap stocks with elevated odds of a 15%+ pop in the next 3-6 weeks. Triggers on phrases like "pre-pop scan", "scan for poppers", "find the next VELO", "pop candidates", "swing watchlist", "weekly screener". Output is a ranked watchlist (top 10-15) with reasons, expected catalyst date, stop, and target. Designed for Yu — small position sizing, hard stops, swing horizon (not scalping).
---

# Pre-Pop Scanner

## Purpose

Find small-cap stocks that look like **VELO did one month before its +17% earnings pop**: beaten down, improving operationally, with a near-term catalyst and squeeze fuel. This is a **watchlist generator**, not a buy-signal generator. Yu reviews each name before sizing.

## When to invoke

- Yu says "pre-pop scan", "scan for poppers", "find the next VELO", "weekly pop screen", "swing candidates"
- Saturday weekly routine (run after `saturday-action`)
- Pre-earnings season prep (mid-Jan, mid-Apr, mid-Jul, mid-Oct)

## The filter stack — run these in order

### Layer 1 — Universe (hard filter)
Use `mcp__3b437285...__search` endpoint `search-company-screener` with:
- `marketCapMoreThan: 100_000_000`
- `marketCapLowerThan: 2_000_000_000`
- `volumeMoreThan: 500_000`
- `isActivelyTrading: true`
- `isEtf: false`, `isFund: false`
- `exchange: "NASDAQ"` (run again for NYSE)

Drop names with: price < $2, country != US, OTC-listed.

### Layer 2 — Catalyst window
For each surviving name, find next earnings date. Sources:
- WebSearch query: `{ticker} earnings date 2026`
- Or use `mcp__3b437285...__statements` endpoint `financial-reports-dates` if plan allows
- **Keep names with earnings in next 3–6 weeks (21–42 days out)**. Drop the rest.

### Layer 3 — Technicals: beaten down but bottoming

For each survivor, pull `historical-price-eod-light` (no date filter — full series) and compute from the last 60 trading days:

- **Distance from 52-wk high**: must be **>30% off high** (washed-out signal)
- **Distance from 52-wk low**: must be **>15% above low** (not falling-knife)
- **RSI(14)**: between **35 and 55** (oversold-to-neutral, not euphoric)
- **20-day SMA reclaim**: current price ≥ 20-day SMA, OR forming higher lows last 10 sessions
- **Volume**: declining on red days vs. green days over last 10 sessions (sellers tiring)

RSI calc (Wilder smoothed):
```
gains = [max(close[i] - close[i-1], 0) for i in last 14]
losses = [max(close[i-1] - close[i], 0) for i in last 14]
avg_gain = mean(gains); avg_loss = mean(losses)
rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
```

**Score 0–3** based on how many of these 5 sub-checks pass.

### Layer 4 — Fundamentals improving

Use `mcp__3b437285...__statements`:
- `income-statement` (period=quarter, limit=4): Revenue growth YoY > 15% AND accelerating QoQ
- `metrics-ratios` (period=quarter, limit=4): Gross margin expanding for 2+ quarters
- `key-metrics` (limit=2): Debt declining or stable; cash runway sufficient

WebSearch fallback: `{ticker} last quarter earnings revenue growth margin`

**Score 0–3** based on: revenue growth, margin expansion, balance sheet health.

### Layer 5 — Smart-money & squeeze fuel

Use `mcp__3b437285...__insiderTrades` and `mcp__3b437285...__analyst`:
- **Insider buying in last 90 days** (any net positive buying): +1
- **Analyst EPS revisions UP last 30 days**: +1
- **Short interest 10–30% of float** (sweet spot for squeeze): +1
- **Strong Buy / Buy consensus**: +1

WebSearch fallbacks (if FMP plan blocks):
- `{ticker} short interest float marketbeat`
- `{ticker} insider buying recent`
- `{ticker} analyst upgrade 2026`

**Score 0–4**.

### Composite score

```
total = layer3_score (0-3) + layer4_score (0-3) + layer5_score (0-4)
max = 10
```

**Cutoff**: keep names with **total ≥ 7**.

Rank by total score descending. If ties, rank by smaller market cap first (smaller = more pop potential).

## Output format

Markdown file at `/outputs/pre-pop-scan-{YYYY-MM-DD}.md` with this structure:

```markdown
# Pre-Pop Scan — {date}

## Top candidates (score ≥ 7)

| Rank | Ticker | Mkt Cap | Earnings ETA | Score | Why interesting | Entry | Stop | Target | Beta/Vol | Gap% | Size %port |
|------|--------|---------|--------------|-------|-----------------|-------|------|--------|----------|------|------------|
| 1 | TICKER | $XXXm | YYYY-MM-DD (Tw) | 9/10 | One-line thesis | $X.XX | $X.XX | $X.XX | 2.3 / 3M | 25% | 1.2% |
| 2 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Sizing column legend** (per Rule 8):
- Beta <1.5: **2.0% port** (assume 15% gap)
- Beta 1.5–2.5: **1.2% port** (assume 25% gap)
- Beta >2.5 OR vol <1M OR price <$5: **0.85% port** (assume 35% gap)
- Biotech/FDA: **0.60% port** (assume 50% gap)

## Filter detail (per name)
For each ticker:
- L1 universe: pass
- L2 catalyst: earnings YYYY-MM-DD
- L3 technical: RSI X, off-high X%, off-low X%, SMA reclaim Y/N → score X/3
- L4 fundamentals: rev growth X% YoY, GM X% (prev Y%) → score X/3
- L5 smart-money: insider buying Y/N, analyst rev Y/N, short int X%, rating → score X/4
- **Catalyst notes**: any recent 8-K, contract news, FDA dates
- **Risk flag**: known overhangs (dilution, lockup expiry, litigation)

## Names that just missed (score 5-6)
Brief table — Yu may want to monitor these.

## Discard log
Tickers that failed Layer 1 or 2 — for audit only, collapsed.

## Macro context
One paragraph on the current tape: are small caps in a risk-on or risk-off regime? Use IWM (Russell 2000) trend vs SPX trend.
```

## Position sizing & risk rules (mandatory in every output)

Print this verbatim at the bottom of every scan:

> **Discipline rules (do not skip):**
> 1. Max **2% of portfolio per position** as initial budget. Never average down.
> 2. Hard stop at **−15%** below entry. Set it the moment you enter.
>    **Acknowledge gap risk**: on small caps, a stop at −15% can fill at −25% to −40% on earnings misses, halts, or 8-K shocks. The stop is a discipline tool, **not a guaranteed loss cap**.
> 3. **Half-position on entry**, add the other half only if it moves +5% in your favor within 5 sessions.
> 4. Maximum **8 open pre-pop positions** at once (you can't track more).
> 5. If earnings miss → exit at open the next day, regardless of price.
> 6. If earnings beat but no pop → exit within 5 sessions at break-even or better.
> 7. **Never hold through a second earnings event**. The setup is one-shot.
> 8. **Gap-aware sizing (the rule that saves you on small caps):**
>    Don't size by the −15% nominal stop. Size by the **realistic gap loss**.
>    ```
>    assumed_gap_loss_pct  = max(15%, 1.5 × stock's 60-day realized daily vol × √5)
>    position_size_dollars = (0.02 × portfolio) / assumed_gap_loss_pct × entry_price
>    ```
>    Quick approximation when you don't have realized-vol handy:
>    - **Liquid, beta < 1.5**: assume 15% gap → full 2% sizing
>    - **Beta 1.5–2.5, avg vol >2M**: assume 25% gap → size at **1.2% of portfolio**
>    - **Beta >2.5 OR avg vol <1M OR price <$5**: assume 35% gap → size at **0.85% of portfolio**
>    - **Biotech / FDA names**: assume 50% gap → size at **0.60% of portfolio**
>    This means you take **smaller positions on more volatile names**, even though they have the same nominal stop. Counterintuitive, but it's the rule that keeps a bad week to −2% instead of −8%.
> 9. **Portfolio-level circuit breaker (the rule that saves your year):**
>    Track cumulative open-position drawdown in a rolling 5-session window.
>    - If open-position drawdown reaches **−4%** of portfolio in 5 sessions → **halt new entries** for 1 week. Existing positions stay (manage to stops).
>    - If drawdown reaches **−6%** of portfolio in 5 sessions → **close ALL open pre-pop positions** at next open, regardless of price, and **suspend the scanner for 2 weeks**.
>    - During suspension: journal what happened (in `/outputs/pre-pop-journal.md`). No new pre-pop trades, no overrides.
>    Resume only after you write down: (a) what went wrong, (b) whether it was bad luck or bad process, (c) what you'll watch for next time.
> 10. **Earnings-week clustering check (before entering):**
>     If 3+ open pre-pop positions already report in the same 5-session window → **do not add a 4th** in that week, even if it scores ≥7. Earnings-week correlation collapses small caps as a basket. Wait for the cluster to clear.

## Expected hit rate — UNKNOWN until out-of-sample validation

**Honest statement**: This skill's hit rate is **not yet known**. The 6 training fixtures (VELO, OWLT, AXTI, PLUG, BYND, LCID) were retrospectively chosen because their outcomes were known. The filter thresholds were tuned to separate them. **Running the skill against those same 6 names cannot validate it — that's in-sample fitting.**

What we can say:
- The filter logic is **plausible** based on factor literature (Minervini, O'Neil, PEAD research).
- Each trade has a defined risk (−15% stop, 2% sizing).
- The asymmetric payoff math (small losses, larger wins) works **at any hit rate ≥30%** — but we don't yet know if this skill achieves 30%.

**What's required before claiming a hit rate**:
1. **Freeze the current thresholds.** No retuning until step 3 completes.
2. **Run live (or paper-trade) for 8–12 weeks** to collect N≥30 picks that the skill flagged at score ≥7.
3. **Score each as WIN (≥+10% within 6 weeks), FLAT, or LOSS (stop hit).** Only this out-of-sample log produces a real hit rate.
4. **Only after step 3** is threshold retuning justified — and only by adding NEW fixtures, never refitting on the original 6.

Until then: trade tiny size or paper-trade. Treat the skill as untested infrastructure, not a proven edge.

Math works **only with disciplined stops + sizing**. If Yu averages down on losers OR claims edge before validating it, this skill loses money.

## Known limitations

1. **Survivorship bias** — case-studies were retrospective. Real-time precision may be lower.
2. **Data gating** — short interest, insider transactions, and EPS revisions need FMP Starter+ tier. With WebSearch fallbacks, Layer 5 accuracy drops ~30%.
3. **Non-earnings pops** (FDA, M&A, partnerships) — this skill catches **earnings-driven** pops well; it'll miss surprise catalysts. Run a separate 8-K monitor for those.
4. **Market regime sensitivity** — pops are common in risk-on tapes (small-caps outperforming), rare in risk-off. The macro context section warns Yu.
5. **Not for scalping** — horizon is 3–6 weeks. If Yu wants intraday plays, use a different skill.

## Workflow when invoked

**Pre-check (run before step 1):**
- Read `/outputs/pre-pop-journal.md` (if exists). Look for:
  - **Active circuit breaker suspension?** If yes and resume date hasn't passed → refuse to run. Output: "Scanner suspended until {date} per Rule 9 circuit breaker. Last drawdown event: {date}. Resume only after writing the journal entry."
  - **Stop-out in last 7 days?** Output a warning at the top of the scan: "⚠️ Recent stop-out detected on {ticker}. Confirm you've journaled the loss before entering new positions."
  - **3+ open positions reporting earnings in same 5-session window?** Add this to the top of the scan: "⚠️ Earnings-week cluster — Rule 10 says no new entries that report on {date_range}."

1. **Confirm with Yu**: "Run the weekly scan for week of {date}?" Wait for ok.
2. **Universe pull** (Layer 1) → typically 800–1,500 names.
3. **Earnings calendar filter** (Layer 2) → typically 80–150 names.
4. **Batch technical scoring** (Layer 3) → typically 25–40 survivors.
5. **Fundamentals + smart-money** (Layers 4–5) → typically 10–20 finalists.
6. **Cutoff at score ≥ 7** → 5–15 top names.
7. **Compute gap-aware sizing per name** (Rule 8) — annotate each row with: assumed gap %, sized position % of portfolio, sized $ amount.
8. **Write output file** to `/outputs/pre-pop-scan-{date}.md`.
9. **Summarize in chat**: top 3 names + 1-line reasons + sizing per name; link to full file.
10. **Offer**: "Want me to schedule this every Saturday at 9am?"

## Training fixtures (DO NOT use for validation)

**Warning**: These 6 names were used to **design** the filter thresholds. Running the skill against them and getting 6/6 correct **proves nothing** — it's in-sample fitting. They are kept only as a **sanity check** that future edits haven't broken the existing logic.

| Ticker | Date (T-30) | Role | Notes |
|--------|-------------|------|-------|
| VELO | 2026-04-12 | training-winner | Pop +17% on 2026-05-12 |
| OWLT | 2026-01-12 | training-winner | Pop on Q4 2025 beat |
| AXTI | 2026-04-01 | training-winner | Pop +35% on Q1 2026 |
| PLUG | 2026-04-12 | training-loser | No improving fundamentals |
| BYND | 2026-04-12 | training-loser | Declining business |
| LCID | 2026-04-12 | training-loser | Cash burn + dilution |

**`--test` behavior**: Scores all 6 and prints "sanity check passed/failed." Failure means a code regression, not a strategy failure. **Do not retune thresholds based on these names** — they are contaminated.

## Holdout validation set (build this over 8–12 weeks)

After each live scan, append every flagged name to `/outputs/pre-pop-holdout.csv` with schema:

```
scan_date, ticker, score, L3_score, L4_score, L5_score, entry_price, stop, target, earnings_date, outcome_30d, outcome_60d, max_drawdown_pct, notes
```

**Validation rule**: After **N≥30 holdout names** accumulate AND ≥4 weeks have passed for the most recent ones, compute:
- Hit rate (% of names with +10% within 6 weeks of flag)
- Win/loss ratio (avg winner % / avg loser %)
- Expectancy per trade ((hit_rate × avg_win) − ((1−hit_rate) × avg_loss))

**Only then** is threshold retuning justified — and the retune must be tested against a FRESH holdout set, never the original 30.

**Until N≥30**: trade tiny size or paper-trade only. The skill is **unvalidated infrastructure**, not a proven edge.

## Notes for Yu (read once, then ignore)

- This skill is a **first-draft v1** with **unproven edge**. Treat every pick as paper-trade size or 0.5% (not the full 2%) until N≥30 holdout names confirm the hit rate is ≥30%.
- **Do not retune the thresholds early.** Retuning before N≥30 is p-hacking — you'll fit to noise and feel smart while quietly losing.
- The honest expectation is **edge unproven, not edge proven**. The asymmetric math works at any 30%+ hit rate, but the skill has not yet demonstrated 30%.
- Pair this with the `saturday-action` skill — pre-pop watchlist generation fits the Saturday slot, and the holdout log review is a natural monthly extension.
- Don't run this if you're emotionally tilted from a recent loss. Tilt + small caps + unvalidated skill = the worst combo possible.

## Failure mode this skill is designed to AVOID

The most dangerous thing a screening skill can do is **claim a hit rate it hasn't earned**, leading you to size up real money against a fictional edge. This skill explicitly refuses to do that — until N≥30 holdout validation completes, the answer to "what's my expected hit rate" is **"unknown."** That's the honest answer, and it's the answer that keeps you solvent long enough to find out.
