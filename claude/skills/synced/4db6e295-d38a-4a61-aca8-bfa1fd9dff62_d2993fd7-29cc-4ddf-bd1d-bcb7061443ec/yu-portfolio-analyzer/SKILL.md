---
name: yu-portfolio-analyzer
version: 5.6.1
last_reviewed: 2026-05-15
description: "Full portfolio analysis for Yu's multi-currency tracker (IDR/SGD/USD). Reads Tracker.xlsx with 13-sheet schema (Dashboard, Overview, SGYahoo, SGLongbridge, SGStockEvent, IDR-Mutual, IDR-Stock, US Moomoo, US Longbridge, US Webull, SnapshotLog, Snapshots), pulls live prices (FMP MCP + Yahoo fallback + Bareksa), computes returns/risk/drift, runs macro + micro research with equity-research sub-skills + Aschenbrenner trendline lens + Kevin Xu geopolitics lens, checks IPS compliance, tracks $1M milestone, generates currency-isolated rebalancing as Markdown. Trigger when Yu uploads a Tracker or asks to: analyze portfolio, check positions, rebalance, review investments, reconcile funds, check returns/risk, screen new ideas, or mentions Makmur/Maribank/LongBridge/moomoo/Webull/Stockbit/Bibit/Endowus/GXS/OCBC or the $1M goal."
---

# Yu's Portfolio Analyzer (v5 — Tracker schema + freshness gate + tilt gates + trade tickets + outcomes log)

## Changelog
- **v5.6.1 (2026-05-15)** — Holdings refresh + clarifications, verified against uploaded `Tracker.xlsx`. **US Moomoo** current rows corrected: BMNR, IAU, META, SOUN, BTC — PYPL closed (Lot 0). **US Longbridge** IREN shown at Lot 0 (position closed; sheet may be empty). **Sheet12** reclassified "empty scratch" → pivot-cache helper (still ignore). **moomoo Stock** explicitly flagged as USD dry powder — account is named "Stock" but `Category=Cash`, must be excluded from any stock analysis. Account rename noted: `LongBridge Balance` → `LongBridge Cash`.
- **v5.6.0 (2026-05-14)** — **Persistence + self-healing fix.** Previously the skill ships as SKILL.md only, but Step 0.5 HARD-FAILED on missing sidecars — an unsatisfiable contract (skill dir is read-only, no sidecars shipped). Now: (1) **Sidecar home is Google Drive** — folder `Portfolio-Analyzer-State` (ID `1KIQdf-Z027GGeqZ_zDHf0LOK_MJLK8Z8`) in Yu's Drive, accessed via the Google Drive connector. State persists across sessions. (2) **Step 0.5 is now self-bootstrapping** — missing sidecar ⇒ create from the embedded default template, never hard-fail; only schema-corruption or unreadable-Drive hard-fails. (3) **Steps 5 & 6 inlined** — the phantom `scripts/returns.py` / `scripts/reconciler.py` references are replaced with inline computation instructions (TWR / Newton-Raphson IRR / NAV-drift). (4) **Steps 2 & 3 price fallback made explicit** — a missing Claude-in-Chrome browser now degrades loudly (`PRICE_UNAVAILABLE` flag) instead of silently failing.
- **v5.5.0 (2026-05-14)** — Tracker SG-sheet + Overview schema refresh (pulled live from the Google Sheet). **SGLongbridge** gained a `Type` column (G) — sparse, `G` tags gold rows (GLS.SI); right-hand anchors `SUM Stock`/`SUM Gold` (H1:I2) + two unlabeled datetime "last pull" anchors (J1, K1). **SGStockEvent** gained a `Type` column (H) — `G` tags the LionGlobal gold row; now carries THREE rows (LionGlobal Gold + PIMCO Maribank + PIMCO Endowus); column B `Name` holds raw un-sanitized HTML scrape fragments (`<!-- -->`, `</h1>`, `<div…>`, `\xa0`, embedded `S$` price) — parser MUST strip HTML before use; right-hand anchors: datetimes I1/K1/L1, numeric SUM J1, `SUM Gold` I2:J2. **SGYahoo** right-hand anchors documented: `Total` value in G1, `Last Pull` datetime H1:I1. **Overview** right-hand panel confirmed spanning cols I–L: FX rates I1:J2, gold price+fetch K1:L2, unlabeled per-currency asset table I4:L7 (GLD/USD/SGD/IDR rows), grand `SUM` at I8/K8. **US Longbridge / US Webull**: `IsGold` column renamed to `Type` (same `G` semantics) — unified with US Moomoo's `TYPE`. Tab order changed (`SnapshotLog` moved to index 4) — name-based parsing unaffected, position-based parsing must not be used.
- **v5.4.1 (2026-05-13 PM5)** — Patch: LSEG (Refinitiv) + S&P Capital IQ MCPs marked SKIP across all on-demand modes. Underlying institutional seats cost USD 15K–30K+/yr/seat — not cost-justified for personal-portfolio book size (would be ~9% of NAV annually for LSEG alone). LSEG-prefixed + sp-global-prefixed sub-skills disabled from auto-trigger. Re-enable only if Yu gains seat access via employer at zero personal cost, or book grows past USD 5M.
- **v5.4.0 (2026-05-13 PM4)** — Replaced the thin "FMP MCP Integration" stub with a full **MCP Data Source Strategy** section. Maps every Step 7 / Topic 2.5 / Step 1.6 input to a specific MCP endpoint with priority order (FMP → LSEG → S&P Global → Google Drive → Claude in Chrome → WebSearch). Adds 16 FMP endpoints not previously referenced: `calendar` (ex-div + earnings + economic + IPO), `analyst` (consensus targets), `news` (corp events), `economics` (CPI / GDP), `insiderTrades`, `form13F`, `senate`, `earningsTranscript`, `secFilings`, `statements`, `technicalIndicators` (RSI for BUY-WINDOW gates), `marketPerformance`, `discountedCashFlow`, `commitmentOfTraders`, `etfAndMutualFunds`, `indexes` (STI quote), `chart` (z-score history). Notes LSEG + S&P Capital IQ need one-time `authenticate` — worth doing for full runs. Per-mode MCP usage table (Quick / Full / Reconcile / Single-name).
- **v5.3.0 (2026-05-13 PM3)** — Explicit BI rate + US rate (Fed funds + EFFR + 3M T-bill + 2Y/10Y/2s10s) tracking in Step 7 Topics 1 & 2. Added dedicated **Topic 2.5 (Singapore signals)** for SGD-bucket recommendations: MAS S$NEER stance, MPS calendar, SORA, SGS curve, iEdge S-REIT index, STI, S-REIT gearing-cap rules, URA property data, PIMCO factsheet checks. Seven new SGD-specific gate rows in Step 12 (MAS tighten/ease, SORA trend, S-REIT P/NAV, STI 200d, MAS gearing cap). `rates_regime` now per-CB (`fed` / `bi` / `mas`) since the three often diverge. Next-release calendar (CPI, FOMC, RDG, MPS) embedded in regime JSON output.
- **v5.2.0 (2026-05-13 PM2)** — Mandatory CPI check every session (Step 7 Topic 0). `inflation_regime` in Step 7.5 must be grounded in actual BLS / FRED / BPS prints, never inferred from Fed posture. Post-CPI auto-review trigger: any recommendation issued in the prior 7 days against a now-stale CPI must be re-evaluated. Next CPI release date surfaces in TL;DR catalysts. Triggered by a live miss: skill inferred "cooling" from Fed pause while Apr-2026 CPI actually printed 3.8% YoY — the matrix gates for gold/REIT adds depend on this label and would have generated wrong adds.
- **v5.1.0 (2026-05-13 PM)** — Emergency-fund floor revised from SGD 30K → SGD 10K reflecting Yu's SGD 15K CC bridge (bridge-only, never carries a balance). Hard gate row + IPS check + Notes + discipline-ladder rung updated. If CC ever rolls a balance, revisit floor immediately.
- **v5.0.0 (2026-05-13)** — Tracker schema rewrite for 13-sheet layout (US Moomoo/Longbridge/Webull, Snapshots, SnapshotLog, Dashboard); freshness gate (Step 4.0); tilt gates (Step 11.5) with cooldown / overtrading / FOMO / decision-card; emergency-fund + wedding-ladder hard gates; trade-tickets table; outcomes log; corporate-action sweep (Step 1.6); versioning + sidecar schema spec.
- **v4.x** — Aschenbrenner/Xu lenses, yesterday's-log check, 4-tier rebalance system, hard FX gates, $1M milestone tracker.
- **v3.x** — Multi-currency bucket isolation, IPS compliance, equity-research sub-skill auto-trigger.
- **v2.x** — FMP MCP integration, Bareksa scrape.
- **v1.x** — Initial Tracker.xlsx reader + Markdown rebalancing output.

End-to-end portfolio analysis for Yu's multi-currency investment portfolio across Indonesia (IDR), Singapore (SGD), and US (USD).

## Yu's Profile

- Risk: Balanced → shifting Growth as $1M target demands higher return
- Horizon: Medium-term (3-7 years), **$1M goal ASAP**
- Base currency: IDR
- Domicile: Singapore (no CGT → TLH gives no benefit)
- Currencies: IDR, SGD, USD
- Key rule: no cross-currency rebalancing. Each bucket rebalanced independently.
- **Monthly savings capacity: VERIFY at session start.** Last confirmed: SGD 2,000/month (2026-05-09). Never assume — ASK if unclear.
- **Investing pattern: Yu is a buyer, not a trader.** Wins came from buying structural names early + holding (gold, NVO). Losses came from late-cycle entries on hyped names (SOUN, BMNR, BTC near $90K, IDX small-caps). Bias every recommendation toward DCA + structural conviction + 3-yr horizon.
- Communication: concise, direct, clear reasoning. No fluff. Yu prefers explain → identify gaps → review/repair → teach back.

## MANDATORY RULES (every session)

1. **FMP MCP first for US prices.** Call `commodity→GCUSD`, `commodity→SIUSD`, `crypto→BTCUSD`, `quote→META`, `quote→PYPL`, `quote→SOFI` via FMP before touching Yahoo. For all other tickers (IDX, SGX, ETFs, small-caps), fall back to Yahoo Finance Chrome JS.
2. **Verify Yu's savings rate** at session start. Default last confirmed value, ASK if it might have changed. Never assume "SGD 20K" or any other legacy figure.
3. **Read yesterday's saturday-action log** before any BUY/SELL/HOLD recommendation (see Step 1.5). Macro freshness threshold: 7 days.
4. **Run macro check** before any BUY/SELL/HOLD. **All 8 Step 7 topics including the dedicated Topic 2.5 (Singapore signals).** Each session must surface: Fed funds target + EFFR + 3M T-bill + 2Y/10Y; BI Rate + next RDG date + IndOGB yields; MAS S$NEER stance + next MPS + SORA + SGS curve + iEdge S-REIT index. DXY, oil, gold, VIX, geopolitics also required. Cross-check matrix in Step 12 references all of these.
5. **Trust the tracker over external data.** When external prices conflict with tracker values, tracker wins unless FMP confirms otherwise.
6. **NAV-only is not the real return.** Always reconcile against total return (with distributions) for IDR mutual funds and bonds.
7. **Markdown only — no Excel** unless Yu explicitly requests it.
8. **Run equity-research sub-skills automatically** in Step 8 for any position with DD > 20% or earnings within 14 days. Don't wait for Yu to ask.
9. **Track $1M milestone every run.** Always show distance to $1M and months-to-target at current savings + return rate.
10. **Enforce FX gates as HARD vetoes** (see Step 12). Recommendations that violate active gates require explicit user opt-in.
11. **Run Step 4.0 freshness gate before any total/drift compute.** If stale > 24h, refresh first or refuse with a "tracker stale, reopen in Google Sheets to refresh GOOGLEFINANCE" instruction.
12. **Run Step 11.5 tilt gates before any BUY emits.** Cooldown / overtrading / FOMO / decision-card are non-negotiable — the late-cycle losers pattern is a behavioural failure mode, not an analytical one.
13. **CPI check is mandatory every session.** Pull actual US headline + core CPI, core PCE, and Indonesia BPS CPI prints. Compute 3m annualized vs 12m trailing. The `inflation_regime` label in Step 7.5 MUST be grounded in real BLS / FRED / BPS data — never inferred from Fed posture or "Fed pause = cooling" shortcuts. **If a CPI release is within 48 hours of today, re-run Step 7.5 and retract any prior-week recommendations whose gate state flipped.** Next CPI release date surfaces in TL;DR catalysts. (Added 2026-05-13 after a session miscalibrated `inflation_regime` to "cooling" when Apr-2026 CPI printed 3.8% YoY — the matrix gates for gold/REIT adds depend on this label.)

## Workflow Execution Contract (per-step budgets, checkpoints, fan-out caps)

Without this contract, a 90-min run that fails at Step 11 wastes all prior work and the agent rushes to finish — silently bypassing gates.

### Per-step time + token budgets (HARD timeouts)

| Step | Time budget | Token budget | On timeout |
|---|---|---|---|
| 0–0.5 (delta + drift) | 2 min | 5K | Skip outcomes review, log warning |
| 1 (read tracker) | 3 min | 10K | Hard-fail; tracker must be readable |
| 1.5 (yesterday's log) | 2 min | 5K | Continue with `prior_anchor: missing` |
| 1.6 (corp action sweep) | 8 min | 20K | Partial; uncovered tickers tagged `EVENT_SCAN_INCOMPLETE` |
| 2 (live prices) | 10 min | 15K | Hard-fail any ticker with no price; do not estimate |
| 3 (Bareksa) | 20 min | 30K | Use cached, mark funds `bareksa_stale` |
| 4 (recalc) | 3 min | 10K | Hard-fail; book total must compute |
| 5 (returns) | 5 min | 15K | Skip per-position IRR for tickers with N<60 |
| 6 (reconcile) | 5 min | 10K | Mark `unreconciled` and continue |
| 7 (macro) | 8 min | 25K | Use cached macro if <7d, else hard-fail |
| 7.5 (regime) | 2 min | 5K | Mark `regime: unclassified`, use static gates |
| 8 (micro + sub-skills) | 15 min | 50K | See fan-out cap below |
| 9 (drift) | 1 min | 3K | n/a |
| 10 (risk) | 3 min | 10K | Skip metrics with insufficient sample |
| 11 (IPS) | 2 min | 5K | Hard-fail; IPS check is non-skippable |
| 11.5 (tilt gates) | 2 min | 5K | Hard-fail; tilt gates non-skippable |
| 12 (recs) | 5 min | 20K | n/a |
| 13 (final) | 5 min | 20K | n/a |
| **Total cap** | **~100 min** | **~265K** | Refuse new sub-skill calls past cap |

### Step 8 Sub-skill Fan-out Cap

| Sub-skill | Max invocations / run |
|---|---|
| `equity-research:thesis` | 3 (highest DD% first) |
| `equity-research:earnings-preview` | 2 (closest earnings first) |
| `equity-research:initiating-coverage` | 1 (new positions only; queue others to next run) |
| `equity-research:model-update` | 2 |
| Aschenbrenner lens | 3 |
| Kevin Xu lens | 2 |
| **Hard ceiling per run** | **10 sub-skill calls total** — past 10, append to `queued_research.jsonl` in the Drive state folder for next session |

### Checkpoint files

After each step that produces durable output, write `checkpoints/<session-id>/step_<n>_complete.json` in the **sandbox working dir** (these are ephemeral, session-scoped — not Drive state) with `{step, completed_at, outputs, next_step_inputs}`. On rerun within 24h within the same sandbox, the skill loads existing checkpoints and resumes — does not redo Bareksa/macro pulls.

### TTL caches

All TTL caches live in the **sandbox working dir** under `cache/` (ephemeral — not Drive state):
- Bareksa: `cache/bareksa_<fund>_<YYYY-MM-DD>.json`, TTL 24h
- Macro (Step 7): `cache/macro_<YYYY-MM-DD>.json`, TTL 24h
- Live rf rates: `cache/rf_rates_<YYYY-MM-DD>.json`, TTL 24h
- FMP quotes: 60 sec in-memory
- Corp-action scan results: 4h

### Progress markers (mandatory)

Emit one line at the start of each step: `[STEP <n>/<13>] <name> — started`. At end: `[STEP <n>/<13>] <name> — done in <m>s, <tokens>tok`. This makes hangs visible.

### Refuse-don't-rush

If total session token use crosses 80% of the cap (~210K) before Step 12, the skill refuses new sub-skill calls and outputs `"BUDGET_GUARD: skipping remaining auto-trigger sub-skills to preserve Step 12+13 quality. Queued: <list>"`. Quality of recommendations > completeness of research.

## Target Allocation (Balanced, Medium-Term → shifting Growth)

### Overall
| Asset Class | Tracker Category mapping | Current Target | $1M-Phase Target | Band |
|---|---|---|---|---|
| Fixed Income | `Bonds` + `Mutual Fund` (FI-tilted: PIMCO, KIM FI, Bibit Bonds) | 35% | 25% | ±5% |
| Equity | `Stock` + `Mutual Fund` (equity-tilted: Amundi, Capital, Insight RE) | 30% | 40% | ±5% |
| Gold | `Gold` (Emas Batang + Maribank Gold + GLS.SI + LionGlobal SG Physical Gold + IAU/GLDM) | 15% | 15% | ±3% |
| Cash/MM | `Cash` (all broker cash sleeves + Maribank Cash Fund + SavePlus) | 10% | 8% | ±3% |
| Crypto | `Crypto` (US Moomoo TYPE=C rows + any BTC/ETH) | 5% | 7% | ±2% |
| Valas (FX) | `Valas` (FX cash holding) | 5% | 5% | ±2% |

> $1M-phase targets apply when Yu explicitly activates growth mode. Current IPS is still Balanced.

### Currency Buckets
- **IDR (~60% of book)**: 40% FI, 35% Equity, 15% Bonds, 10% Cash
- **SGD (~35% of book)**: 50% FI, 20% Equity (REITs), 15% Gold, 15% Cash
- **USD (~5% of book)**: 35% Equity, 25% Gold/Silver, 20% Crypto, 20% Cash/Valas

---

## Workflow (runs on every Tracker upload)

### Step 0 — Delta vs last snapshot
**Primary source: `Snapshots` sheet inside the Tracker itself** (built-in history, currency-preserved). Read the latest timestamp's rows, then the prior one, and diff. Fallback: `last_snapshot.json` from the Drive state folder (see Sidecars section) only if the Snapshots sheet is missing or empty. Report new/removed positions, qty/price changes, FX moves. Save new snapshot back to `last_snapshot.json` at end.

### Step 0.5 — Sidecar bootstrap + outcomes-log review (MANDATORY, self-healing)

All sidecars live in the **Google Drive state folder** `Portfolio-Analyzer-State` (ID `1KIQdf-Z027GGeqZ_zDHf0LOK_MJLK8Z8`), accessed via the Google Drive connector. This step is self-healing — it never hard-fails on *missing* files, only on *corrupt* ones.

1. **Locate the state folder.** Via the Drive connector, confirm folder ID `1KIQdf-Z027GGeqZ_zDHf0LOK_MJLK8Z8` is reachable. If the connector is unavailable → HARD-FAIL ("Google Drive connector not connected — needed for portfolio state"). If the folder ID 404s → search Drive for a folder named `Portfolio-Analyzer-State`; if still not found, create it in the user's My Drive and note the new ID in the run output.
2. **Bootstrap each sidecar.** For every file in the Sidecars table:
   - **Missing** → create it in the state folder from the embedded default template (see "Bootstrap templates" in the Sidecars section). Log `BOOTSTRAPPED: <file>`. Do **not** hard-fail. If the template has `_todo` fields, surface them in the TL;DR as "setup needed".
   - **Present + parses + schema-valid** → load it. WARN (don't fail) if `_meta.last_updated` is older than its stale threshold.
   - **Present but unparseable / schema-corrupt** → HARD-FAIL with `"Schema drift: <file> — <diff>"`. Corruption is the only hard-fail; absence is not.
3. Scan `outcomes.jsonl` for entries needing 30/90/180-day price reviews; fill them in by pulling the current price, write the file back to Drive.
4. Compute rolling hit-rate per tier + per action over the trailing 6 months. If current hit-rate drifts > 1σ from the trailing baseline, surface in TL;DR risk bullet (the skill itself may be miscalibrated). Skip silently if `outcomes.jsonl` has fewer than 5 real entries.
5. **Write-back rule:** any sidecar mutated during the run (logs appended, snapshot saved, flags updated) is written back to the Drive state folder before Step 13 completes, with `_meta.last_updated` refreshed.

### Step 1 — Read Tracker
Read uploaded `Tracker*.xlsx` with `openpyxl(data_only=True)`. Read ALL positions dynamically.

**Sheets (current schema — May 2026):**

| Sheet | Purpose | Key columns / anchors |
|---|---|---|
| **Dashboard** | Live snapshot view — category subtotals, Top Movers (1H + 1D, by Label + by Category), SGD/IDR 30-day close history | Cols B-H: Category/Subtotal/Composition + movers tables |
| **Overview** | Master positions table per broker/account (authoritative) | R1 header (cols A-H): `Type, Category, Grams, USD, SGD, IDR, Subtotal, Composition`. Right-hand panel spans **cols I-L**: FX rates `SGD-IDR` (I1)=J1, `USD-IDR` (I2)=J2; gold `Gold 1 Gram` (K1)=L1, `Gold Last Fetch` (K2)=L2 datetime; an unlabeled per-currency asset table at **I4:L7** (rows `GLD / USD / SGD / IDR`, cols = native amount / value-IDR / composition%); grand `SUM` at **I8** with total NAV in **K8**. **Look up rates and totals by label, NOT fixed cell coords — layout will drift.** |
| **SGYahoo** | Yahoo-priced SG funds | `Code, Name, Price, Qty, Subtotal, Total` — holds Maribank SavePlus (`0P0001RAKU.SI`) + Amundi MSCI World (`0P0001OO2D.SI`) + Amundi MSCI EM (`0P0001OO2F.SI`). Right-hand anchors: total value in **G1** (the `Total` label sits in F1, value to its right), `Last Pull` datetime at **H1:I1**. |
| **SGLongbridge** | SGX-listed via LongBridge | `Code, Qty, COST, Name, Price, Subtotal, Type` — **`Type` col (G) is sparse: `G` tags gold rows.** A35.SI (ABF SG Bond), G3B.SI (Amova STI ETF, formerly Nikko AM), CLR.SI (Lion-Phillip S-REIT), GLS.SI (LionGlobal SG Physical Gold, `Type=G`). Right-hand anchors: `SUM Stock`/`SUM Gold` key-value pairs at **H1:I2**, two unlabeled datetime "last pull" anchors at **J1** and **K1**. |
| **SGStockEvent** | PIMCO + LionGlobal Gold | `ID, Name, Price, Drift Endowus, Unit, Subtotal, Notes, Type`. **`Notes` col (G)** tags Maribank vs Endowus; **`Type` col (H)**: `G` tags the gold row. **THREE rows:** LionGlobal SG Physical Gold (`SGXZ19297886.FUND`, `Type=G`), PIMCO Income (`IE00B91RQ825.FUND`) Maribank, PIMCO Income Endowus. **⚠ Column B `Name` holds raw un-sanitized HTML scrape fragments** (`<!-- -->`, `</h1>`, `<div…>`, `\xa0`, embedded `S$` price) — strip HTML/whitespace before display or matching. Right-hand anchors: datetime anchors at I1/K1/L1, numeric SUM at J1, `SUM Gold` key-value at I2:J2. |
| **IDR-Mutual** | Makmur / Bibit / Bareksa mutual funds | Cols A-D: fund registry. Cols G-K: holdings (`Source, Fund, Unit, Subtotal, Sum`) |
| **IDR-Stock** | IDX stocks | `Stock, Lot, COST, Price, Total`. 1 lot = 100 shares |
| **US Moomoo** | US holdings on Moomoo | `Stock, Lot, COST, Price, Total, TYPE`. **TYPE column classifies:** blank = Stock, `G` = Gold (e.g. IAU), `C` = Crypto. Right-side anchors: `SUM Stock`, `SUM Gold`, `SUM Crypto`. Current: BMNR, IAU, META, SOUN, BTC. PYPL closed (Lot 0) |
| **US Longbridge** | US holdings on LongBridge | `Stock, Lot, Cost, Price, Total, Type` (col header was `IsGold` pre-v5.5 — now `Type`, same `G` semantics). Right-side anchors: `SUM Stock`, `SUM Gold`, `SUM Crypto`. Current: IREN (Lot 0 — position closed; sheet may be empty) |
| **US Webull** | US holdings on Webull | `Stock, Lot, COST, Price, Total, Type` (col header was `IsGold` pre-v5.5 — now `Type`, same `G` semantics). Right-side anchors: `SUM Stock`, `SUM Gold`, `SUM Crypto`. Current: NVO, SOFI, GLDM (`Type=G`) |
| **SnapshotLog** | Time-series audit log (rolled-up per account+category) | `Timestamp, Date, Hour, Account, Category, Value_IDR` — one row per snapshot per account per category. Use for drift/TWR. |
| **Snapshots** | Time-series audit log (currency-preserved) | `Timestamp, Label, Category, Total, OriginalValue, Currency` — preserves native currency. Use for currency-bucket return calcs. |
| **Sheet12** | Pivot-cache helper — ignore | — |

**Read order:**
1. Open workbook with `openpyxl(data_only=True)`
2. Build rates dict from Overview cols I-L by scanning for labels `SGD-IDR`, `USD-IDR`, `Gold 1 Gram`, `Gold Last Fetch`, `SUM`, and the per-currency rows (`GLD`, `USD`, `SGD`, `IDR`) in the I4:L8 panel
3. Pull positions per-sheet using the column map above
4. For US sheets: combine Moomoo + Longbridge + Webull rows; split by the `TYPE`/`Type` column (`G`=Gold, `C`=Crypto, blank=Stock) into Stock vs Gold vs Crypto buckets
5. For SG sheets: SGLongbridge + SGStockEvent now both carry a `Type` column — `G` flags gold rows (route to Gold bucket, not Stock/Mutual Fund). Strip HTML from SGStockEvent col B before use.
6. For history: prefer `Snapshots` (currency-preserved) over `SnapshotLog` when computing currency-bucket returns
7. Resolve sheets by NAME, never tab index — tab order changed in the May-2026 tracker (`SnapshotLog` moved up)

### Step 1.5 — Read yesterday's saturday-action log + macro snapshot

**Mandatory before any recommendation.** Locate and read:
- Most recent saturday-action checkpoint or daily log (look in user's tracker outputs / chat history)
- Most recent macro snapshot from prior session

**Cross-check rules:**
- If today's macro view contradicts yesterday's log without new news to justify the flip → FLAG and ask user before recommending.
- If last macro pull > 7 days old → refresh via Step 7 before recommendations.
- Yesterday's specific BUY/SELL/HOLD calls are the prior anchor — don't whiplash without explicit cause.

**Why this matters:** Stale macro framing has caused recommendation flip-flops (e.g., "avoid CLR — Fed hawkish" while yesterday's log said "DCA CLR — Fed near-dovish"). Honor the prior anchor or explain what changed.

### Step 1.6 — Corporate Action & Event Sweep (MANDATORY)

Run BEFORE Step 2 price-pull. Catches the failure mode where stale ticker/cost-basis assumptions silently corrupt every downstream metric. Generalized — not a list of one-offs.

**Checks (run all, in order):**

1. **Ticker rebrand / ISIN reuse**
   - For each ticker in the Tracker: look up current name/ISIN via Yahoo or FMP, compare against `ticker_history.json` (Drive state folder).
   - If name or ISIN changed AND no entry in ticker_history → FLAG `REBRAND_UNVERIFIED`, write proposed entry, require user confirm before continuing.
   - (Example precedent: G3B.SI Nikko AM → Amova.)

2. **Stock split / reverse split detector**
   - For each equity ticker: compare today's price vs prior session's close.
   - If `|today / prior - 1| > 0.40` AND no news event ⇒ FLAG `SPLIT_SUSPECTED`. Require user to confirm split ratio and recompute cost basis before any TWR/IRR runs in Step 5.
   - (1:10 split would silently misalign cost basis in IDR-Stock / US Webull and corrupt the $1M tracker.)

3. **Ex-dividend / distribution sweep**
   - Pull next-30-day ex-div calendar for every holding (not just IDR funds). FMP `dividends-calendar` for US/SG; Bareksa fund factsheet for IDR MFs.
   - Mark NAV-only-vs-total-return reconciliation requirement on every fund/stock with an ex-div in trailing 30d.

4. **M&A / delisting / going-concern**
   - WebSearch each holding `"<ticker> merger OR acquisition OR delisting OR going concern OR Chapter 11"` with last-7-day filter.
   - Any hit ⇒ FLAG `CORP_EVENT` and override the position's recommendation to MONITOR until resolved.

5. **Index inclusion / removal**
   - Check MSCI, FTSE Russell, S&P Dow Jones rebalance calendars. (BREN/DSSA precedent.) Hit ⇒ flag.

6. **Lockup / restriction expiry**
   - For every Makmur 100-wk locked position: compute days-to-unlock. If ≤ 30 days, surface in TL;DR — a tradeable window is opening.
   - For any IPO/secondary holding: flag lockup expiry within 30 days.

7. **Per-currency market-open calendar**
   - For each currency bucket, read today's market status (IDX = Jakarta, SGX = Singapore, NYSE/NASDAQ = New York). If a bucket is closed, all prices for that bucket get tagged `LAST_TRADING_DAY_CLOSE` and freshness gate (Step 4.0) accepts up to 72h for that bucket only.

8. **Partial-fill reconciliation**
   - Diff each broker's cash delta (since prior snapshot) vs sum of expected trade executions. If unaccounted ⇒ FLAG `UNRECONCILED_FILL` and pause recommendations for that broker bucket until cleared.

**Outputs Step 1.6 produces:**
- `corporate_actions_<YYYY-MM-DD>.json` — one entry per flagged event with `{ticker, type, severity, action_required}`
- A `block_recommendations_for` list of tickers with unresolved CORP_EVENT / REBRAND_UNVERIFIED / UNRECONCILED_FILL — Step 12 must downgrade these to MONITOR.

**Why this matters:** A 1:10 split, an unflagged ISIN swap, or a missed lockup release directly corrupts TWR/IRR (Step 5), drift (Step 9), and the $1M tracker (Step 13). The Amova/BREN/BUMI rebrand+removal cases are not unique — they are samples from a generalized class of events the skill must detect, not enumerate.

### Step 2 — Live price verification (FMP MCP first, Yahoo fallback)

**Priority order:**

| Ticker group | Source | Tool |
|---|---|---|
| Gold | **FMP MCP** `commodity→GCUSD` | Always — most accurate |
| Silver | **FMP MCP** `commodity→SIUSD` | Always |
| BTC | **FMP MCP** `crypto→BTCUSD` | Always |
| META, PYPL, SOFI | **FMP MCP** `quote→{symbol}` | Always (free tier) |
| IREN, NVO, SOUN, BMNR | Yahoo Finance Chrome JS | FMP restricted on free tier |
| IAU, GLDM, IAUM, SLV | Yahoo Finance Chrome JS | ETFs restricted on FMP free |
| IDX stocks (.JK) | Yahoo Finance Chrome JS | Not on FMP free |
| SGX stocks (.SI) | Yahoo Finance Chrome JS | Not on FMP free |
| USD/IDR, SGD/IDR | xe.com / WebSearch | FMP forex restricted |

**Fallback chain (degrade loudly — never silently estimate):**
`FMP MCP → Yahoo via Claude in Chrome → WebSearch → tag PRICE_UNAVAILABLE`.

- **Before relying on the Chrome leg, probe it:** call the Claude-in-Chrome connector's `list_connected_browsers`. If no browser is connected (computer use disabled, or no Chrome session), the Yahoo leg is DOWN — do not retry it per-ticker.
- When the Chrome leg is down: FMP still covers gold (`commodity→GCUSD`), silver (`commodity→SIUSD`), BTC (`crypto→BTCUSD`), and the free-tier US names (META, PYPL, SOFI). **Every ticker FMP cannot price — all `.JK` (IDX), all `.SI` (SGX), restricted US ETFs — gets explicitly tagged `PRICE_UNAVAILABLE`**, carried at last tracker value, and listed in the TL;DR data-quality bullet. Never interpolate or guess a price.
- A run with any `PRICE_UNAVAILABLE` ticker is a **partial run**: Step 12 may still recommend on fully-priced buckets but must downgrade any position touching a stale price to MONITOR.

### Step 3 — Bareksa scrape (IDR funds)

Bareksa pricing also depends on the Claude-in-Chrome browser leg. **Probe it once at the start of this step** (reuse the `list_connected_browsers` result from Step 2).

**If the browser leg is available**, for each fund in `fund_registry.json`:
1. Navigate `bareksa.com/reksadana/data-reksadana/<slug>` → extract NAV, returns, distributions, TER, top holdings.
2. Save raw to the Drive state folder as `raw_<YYYY-MM>.json`.
3. Fallback per fund: Pasardana → manager factsheet → WebSearch.
4. Time budget: 90 min. If over, mark the fund "unverified" and continue.

**If the browser leg is DOWN**, do not silently skip: tag every IDR mutual fund `PRICE_UNAVAILABLE`, carry it at last tracker NAV, surface a single TL;DR line ("IDR mutual-fund NAVs not refreshed — Claude in Chrome not connected; enable computer use + connect a browser, or refresh the Tracker's GOOGLEFINANCE in Google Sheets"), and continue. The IDR bucket's drift/return numbers are then flagged `bareksa_stale` for the rest of the run.

### Step 4 — Recalculate portfolio

**Step 4.0 — Freshness gate (MANDATORY, fail-closed).** Before computing anything:

1. **Read every timestamp anchor:** Overview `Gold Last Fetch` (L2), `Last Pull` on SGYahoo (I1), the two unlabeled datetime anchors on SGLongbridge (J1, K1), the unlabeled datetime anchors on SGStockEvent (I1, K1, L1), `Timestamp` on the most recent Snapshots row, `Updated:` on Dashboard tiles. (SG-sheet timestamps are positional, not label-keyed — read them by column position, take the oldest as the bucket's freshness.)
2. **Refuse-and-refresh if ANY anchor > 24h old OR missing.** Refresh FX via xe.com (USD/IDR + SGD/IDR), gold via FMP `commodity→GCUSD`, US single-names via FMP `quote→{symbol}`, ETFs/IDX/SGX via Yahoo Chrome JS. Re-read the Tracker after the user has reopened it in Google Sheets so GOOGLEFINANCE recomputes.
3. **Sanity bounds** — hard-fail (do not silently coerce) if:
   - Any price is zero, negative, NaN, or null
   - USD/IDR < 10,000 or > 20,000
   - SGD/IDR < 9,000 or > 16,000
   - Gold/gram IDR < 1,000,000 or > 4,000,000
4. **Authoritative total resolution:** trust Overview's labeled `SUM` cell ONLY if (a) freshness gate passed AND (b) it matches Dashboard's `Grand Total` within 0.1%. If they diverge or either is stale, the **recomputed-from-positions total** (sum of all individual holdings priced live) becomes canonical and both stale figures are surfaced in the report with their inferred timestamps.

All positions → IDR using live prices + FX. Group by category AND currency bucket.

**Category taxonomy** (matches Overview's `Category` column):
- `Bonds` (Bibit SBN/FR)
- `Cash` (GXS, OCBC, Endowus cash, Maribank Cash Fund, Stockbit, Webull Cash, LongBridge Cash, **moomoo Stock = USD dry powder** — account named "Stock" but `Category=Cash`; exclude from stock analysis)
- `Crypto` (US Crypto via US Moomoo TYPE=C)
- `Gold` (Emas Batang grams, Maribank Gold, LionGlobal Gold via SGStockEvent + GLS.SI via SGLongbridge, US Gold ETFs via TYPE=G/IsGold=G)
- `Mutual Fund` (IDR Reksadana / Makmur / Bibit MF, PIMCO via SGStockEvent, Amundi via SGYahoo)
- `Stock` (IDR-Stock, SGLongbridge equity portion, US Moomoo + Longbridge + Webull stock rows)
- `Valas` (FX cash holding — new category)

### Step 5 — Compute returns (TWR/MWR/CAGR/IRR)

Compute inline (write a short Python snippet in the sandbox — there is no bundled `scripts/returns.py`). Use the `Snapshots` sheet for the cash-flow timeline and the Tracker cost-basis columns. For every position with a cost basis:
- **TWR** — chain-link sub-period returns between snapshots; strips cash-flow timing. Compare to the bucket benchmark.
- **MWR/IRR** — solve `Σ CF_t / (1+r)^t = 0` by Newton-Raphson (seed r=0.1, ≤50 iterations, tol 1e-6); fall back to bisection on [-0.99, 5.0] if it fails to converge. This is the real experienced return.
- **CAGR** — `(end/start)^(1/years) − 1` since entry.
- **MOIC** — current value / total cost (equity positions).

**Invoke the `private-equity:returns-analysis` sub-skill for:**
- Any position held > 12 months: IRR + MOIC sensitivity table.
- Show base / bull (+20%) / bear (−20%) exit scenarios.
- Flag any position where IRR < blended risk-free rate (5.0%) → capital misallocation.

Output: write `return_calc_<YYYY-MM>.json` to the Drive state folder.

### Step 6 — Fund reconciliation

Compute inline (short sandbox snippet — there is no bundled `scripts/reconciler.py`). For each IDR mutual fund, using Bareksa data from Step 3 (or `bareksa_stale` last values if the browser leg was down):
- **NAV drift check** — tracker NAV vs Bareksa NAV; flag if |diff| > 0.5%.
- **Total return vs NAV-only** — real 1Y total return (with distributions) minus NAV-only return = the distribution gap; never report NAV-only alone (MANDATORY RULE 6).
- **Peer comparison** — 1Y return vs peer-median for the fund's category.

Flags: `distributing`, `underperform-benchmark`, `high-ter`, `laggard-vs-peers`, `nav-drift`. If the fund is `bareksa_stale`, also tag `unreconciled` and skip the peer comparison.

### Step 7 — Macro research

Run all 8 topics (WebSearch). **Topic 0 (CPI) is mandatory every session — no exceptions.**

0. **US CPI / Inflation (MANDATORY — never skip):**
   - Pull latest BLS CPI release: headline YoY, core YoY (ex food + energy), monthly headline %, monthly core %, energy YoY contribution
   - Compute **3-month annualized** vs **12-month trailing** — divergence > 50bps = regime shift signal
   - Cross-ref Cleveland Fed nowcast for the next release
   - Pull next BLS CPI release date (~mid-month for prior month) — surface in TL;DR catalysts
   - Also pull: core PCE (Fed's preferred measure, ~monthly), Indonesia BI CPI (BPS release, ~beginning of month), Singapore MAS CPI (~late month)
   - **This input is the dominant driver of `inflation_regime` in Step 7.5. Do not infer "cooling" from a Fed pause — pull the actual print.**
1. **US interest rates (MANDATORY — explicit prints, not vibes):**
   - **Fed funds target range** (e.g. 3.50–3.75%) + **effective Fed funds rate (EFFR)** — FRED `FEDFUNDS` / `EFFR`
   - **3M T-bill yield** (used as USD risk-free in Step 10 Sharpe) — FRED `DTB3`
   - **2Y Treasury yield** (Fed expectations) — FRED `DGS2`
   - **10Y Treasury yield** + **2s10s spread** — FRED `DGS10`, `T10Y2Y`
   - **Next FOMC date** + dot-plot from latest SEP + dissent count from most recent statement
   - Fed leadership signals: Powell statements, Warsh / political pressure, voting member shifts
   - Read: hiking / holding / cutting / "hawkish hold" / "dovish hold" — label feeds `rates_regime` in Step 7.5
2. **Bank Indonesia (BI) + IDR (MANDATORY — explicit prints):**
   - **BI Rate** (BI 7-Day Reverse Repo) — current level + last 3 decisions — Bank Indonesia `bi.go.id` / FRED `INTDSRIDM193N`
   - **Next BI Board of Governors meeting** ("Rapat Dewan Gubernur" / RDG — typically 17–20th of each month)
   - **USD/IDR** + 90d trend (z-score feeds Step 7.5 + USD/IDR > 17,000 hard gate)
   - **Indonesia headline CPI YoY** (BPS, ~beginning of each month) — already in Topic 0
   - **JIBOR / IndONIA rates** — short-end IDR funding cost — bi.go.id
   - **INDOGB 3M + 10Y yields** — IDR rf input for Step 10 + macro context — Indonesia DJPPR / Bloomberg
   - **MSCI / FTSE Indonesia rebalances** (BREN/DSSA precedent) — flag any IDX-Stock holding in scope
   - **Mineral tax / ESDM regulations** — BUMI, ANTM, INCO directly exposed
   - Read: BI hawkish/dovish + rupiah strength → feeds IDR equity gate calibration
3. **Singapore signals (MAS + SGX) — see Topic 2.5 (new dedicated section below)**
4. Gold spot + trend + CB buying (cross-ref FMP GCUSD)
5. Oil (Brent/WTI) + OPEC + disruptions
6. Geopolitics (wars, sanctions, energy infra, Indonesia mineral tax, US-China chip war)
7. S&P 500 + VIX regime + AI capex pulse
8. Crypto (BTC/ETH + flows + F&G) (cross-ref FMP BTCUSD)

#### Topic 2.5 — Singapore signals (MANDATORY for SGD-bucket recommendations)

Yu's SGD bucket is ~35% of book and contains rate-sensitive instruments (PIMCO Income, ABF SG Bond `A35.SI`, Lion-Phillip S-REIT `CLR.SI`, LionGlobal Physical Gold `GLS.SI`, Amova STI ETF `G3B.SI`, Amundi MSCI World / EM, Maribank SavePlus + Cash Fund + FI Fybd). Generic US macro doesn't capture what moves these. Pull the following every session:

| Signal | Source | Why it matters |
|---|---|---|
| **MAS Monetary Policy Statement (MPS)** — next release date + last stance (tighten / hold / ease the S$NEER band) | [MAS](https://www.mas.gov.sg/news/monetary-policy-statements) (semi-annual, April + October; can be off-cycle) | MAS uses exchange-rate policy not interest rates — a stronger SGD band tightens financial conditions, hurts exporters (G3B.SI tilt), helps importers and S-REITs (cheaper foreign capex) |
| **SORA** (Singapore Overnight Rate Average — replaces SIBOR/SOR) — 3M compounded + 6M compounded | [MAS SORA page](https://www.mas.gov.sg/monetary-policy/sora) / ABS Benchmarks | Used as SGD rf in Step 10 Sharpe (replaces hardcoded 3.5%). Also pulse on S-REIT financing costs |
| **SGS yield curve** (Singapore Government Securities) — 3M, 2Y, 10Y, 30Y | [MAS](https://eservices.mas.gov.sg/statistics/) | Directly priced into A35.SI (ABF SG Bond ETF). 2s10s and curve steepening = bond bull/bear signal |
| **Singapore CPI YoY (headline + MAS core)** | BPS-equivalent: [SingStat](https://www.singstat.gov.sg) / MAS | Already in Topic 0. MAS core (ex accommodation + private transport) is what MAS targets — track separately from headline |
| **STI (Straits Times Index)** — level + 50d / 200d MA + 1Y total return | Yahoo `^STI` or FMP | Direct driver of G3B.SI (Amova STI ETF). 200d MA cross = trend filter |
| **S-REIT sector signals (CLR.SI driver):** | | |
|   – **iEdge S-REIT Index** level + dividend yield + price-to-NAV | [iEdge index page](https://www.sgx.com/indices/products/sreit) / SGX | CLR.SI tracks Lion-Phillip selection of S-REITs. Price-to-NAV < 0.85 historically = oversold; > 1.10 = overvalued |
|   – **MAS REIT rules / leverage cap** changes (currently 50% gearing cap) | MAS press releases | Any tightening to 45% = forced delevering across S-REITs; loosening = sector tailwind |
|   – **SG commercial property — URA quarterly index** (office, retail rentals) | [URA](https://www.ura.gov.sg/Corporate/Property/Property-Data) | Lagged but predictive of S-REIT NAV writedowns |
|   – **BSD/ABSD changes** (Buyer's Stamp Duty / Additional BSD) | IRAS / cooling measure announcements | Residential REITs / property exposure |
| **STI / SGX top holdings** — DBS, OCBC, UOB earnings + dividend declarations | SGX company announcements | Bank-heavy STI means G3B.SI moves with bank quarterlies. Track ex-div dates per Step 1.6 #3 |
| **PIMCO Income Fund flows + duration + credit positioning** — monthly factsheet | [PIMCO Income](https://www.pimco.com.sg) | Largest single fund (~20-23% of book). Duration extension into rate-cut cycle = hold; duration compression + cash build = mgmt sees stress |
| **Amundi MSCI World / EM monthly factsheet** | Endowus / Amundi site | Tracking-error vs benchmark, AUM trends |
| **SG geopolitics signals** | WebSearch | SG-China trade (50% of GDP), US tariffs on transhipment, Malaysia ringgit weakness, ASEAN cross-currents |

**Singapore-specific gate hooks (additions to Step 12 cross-check matrix):**

| If... | Then... |
|---|---|
| **MAS tightens S$NEER band** (next MPS or off-cycle) | SGD strengthens → DCA Amundi MSCI World OK; CLR.SI add-window narrows (S-REITs hurt by stronger SGD = weaker overseas asset translations) |
| **MAS eases S$NEER band** | SGD weakens → exporters help (some STI components); but Yu's USD-denominated assets (US Stock, US Gold, BTC) get cheaper in SGD terms — opportunistic add window |
| **SORA 3M trending down ≥ 50bps over 3 months** | Rate-cut tailwind → CLR.SI add (S-REIT financing cheaper); A35.SI (SG bond duration) extension; PIMCO duration stays elevated |
| **SORA 3M trending up ≥ 50bps over 3 months** | Hawkish drift → trim CLR.SI on strength; shorten A35.SI duration |
| **iEdge S-REIT price-to-NAV < 0.85** | Sector capitulation BUY-WINDOW for CLR.SI (overrides regime if no other gate trips) |
| **STI 200d MA breached to downside + RSI < 30** | G3B.SI / Amundi MSCI World opportunistic DCA window |
| **MAS gearing cap tightens from 50% → 45%** | HARD GATE: S-REIT adds BLOCKED for 90 days (forced delevering supply); revisit when cap stabilises |

**Singapore-specific notes:**
- **No CGT in SG** — TLH gives no tax benefit but also no exit-tax penalty. Be more willing to trim losers cleanly (unlike US tax-lot games).
- **MAS-regulated brokers** (LongBridge, moomoo SG, Webull SG, Endowus, Maribank, GXS, OCBC) — all CDP-linked or omnibus. Custody risk is low; counterparty stratification not needed.
- **Distribution timing** — PIMCO Income distributes monthly; Amundi accumulating share class reinvests automatically. NAV-only return understates total return on PIMCO meaningfully (Rule 6 applies).

**Post-CPI auto-review trigger:** if today is within 48 hours of a CPI release date, the skill MUST re-run Step 7.5 (regime classification) before any Step 12 recommendation. Recommendations issued in the prior 7 days against a now-stale CPI must be re-evaluated and explicitly retracted if the gate state flipped.

### Step 7.5 — Regime classification (MANDATORY, feeds Step 12 gates)

Static univariate thresholds (USD/IDR > 17,000, VIX > 25, F&G > 75) work fine in one regime and fail badly in another. Compress Step 7's raw inputs into a 4-dimensional regime label that Step 12 gates consume directly.

**Inputs (60-day rolling windows unless noted):**

| Signal | Source | Window |
|---|---|---|
| DXY | WebSearch / FMP | 60d |
| VIX | WebSearch / FMP | 60d |
| HY-OAS (US high-yield option-adjusted spread) | FRED `BAMLH0A0HYM2` via WebSearch | 60d |
| 2s10s curve | FRED `T10Y2Y` via WebSearch | 60d |
| Oil-vol (OVX) | WebSearch / FMP | 60d |
| USD/IDR | xe.com | 90d |
| **US headline CPI YoY** | **BLS release (~mid-month) / FRED `CPIAUCSL`** | **24m trend + last 3 prints** |
| **US core CPI YoY** | **BLS / FRED `CPILFESL`** | **24m + last 3** |
| **US core CPI 3m annualized** | **BLS / FRED** | **derived from monthly prints** |
| **US core PCE YoY** | **BEA / FRED `PCEPILFE`** | **24m + last 3** |
| **Indonesia headline CPI YoY** | **BPS via WebSearch** | **last 3 prints** |
| **Singapore CPI YoY** | **MAS via WebSearch** | **last 3 prints** |
| **Next CPI release date** | **BLS calendar / [investing.com](https://www.investing.com/economic-calendar/cpi-69)** | **forward 30d** |
| **US Fed funds target + EFFR + 3M T-bill + 2Y / 10Y / 2s10s** | FRED `FEDFUNDS`, `EFFR`, `DTB3`, `DGS2`, `DGS10`, `T10Y2Y` | 60d + last 3 |
| **BI Rate (7-Day Reverse Repo) + next RDG date + JIBOR + INDOGB 3M/10Y** | [bi.go.id](https://www.bi.go.id) / FRED `INTDSRIDM193N` | 12m + forward 30d |
| **MAS S$NEER band stance (last MPS + next MPS date)** | [MAS](https://www.mas.gov.sg/news/monetary-policy-statements) | last 2 MPS prints |
| **SORA 3M compounded + 6M compounded + SGS 3M/2Y/10Y yields** | [MAS](https://www.mas.gov.sg/monetary-policy/sora) + SGS curve | 60d |
| **iEdge S-REIT index level + price-to-NAV + STI level** | SGX / iEdge | 60d + 200d MA |

**Compute z-scores** of today's value vs 60d mean & stdev for each signal.

**Output regime labels:**

| Dimension | Buckets | Rule |
|---|---|---|
| `risk_regime` | `risk_on` / `neutral` / `risk_off` | `risk_off` if VIX z > +1 AND HY-OAS z > +1; `risk_on` if VIX z < -0.5 AND HY-OAS z < -0.5; else `neutral` |
| `rates_regime` | `hiking` / `holding-hawkish` / `holding-neutral` / `holding-dovish` / `cutting` — per CB | **Classify each of Fed / BI / MAS separately** (they often diverge). Rule: read forward guidance + last 3 decisions + dot-plot (Fed) / RDG statement (BI) / MPS stance (MAS). `holding-hawkish` requires explicit hike-risk language or dissents on hawkish side; `holding-dovish` requires cut-language without dissents. Output as `{fed: ..., bi: ..., mas: ...}` so Step 12 gates can reference per-bucket. |
| `inflation_regime` | `accelerating` / `cooling` / `sticky` | **Pull actual CPI prints (Step 7 Topic 0). Decision rule:** `accelerating` if (US core CPI 3m annualized > 12m trailing by ≥ 30bps) OR (last 2 headline prints both higher MoM); `cooling` if (core 3m annualized < 12m trailing by ≥ 30bps) AND (energy YoY trending down); `sticky` otherwise. **Never infer from Fed pause/posture — pull the BLS data.** |
| `crisis_flag` | `false` / `true` | `true` if `VIX > 40 AND HY-OAS > 800bps` simultaneously |

**Relative thresholds (replace static absolutes — fallback to static if z-score unavailable):**

| Gate | Static (fallback) | Relative (preferred) |
|---|---|---|
| IDR equity block | USD/IDR > 17,000 | USD/IDR z > +1.5 over 90d |
| USD equity block | VIX > 25 + recession > 30% | `risk_regime = risk_off` AND `crisis_flag = false` |
| BTC adds block | F&G > 75 | F&G z > +1.2 over 90d |
| Gold add window | Oil < $90 | Oil z < -0.5 AND `rates_regime` ∈ {holding, cutting} |
| SG REIT add | Fed dovish + oil stable | `rates_regime = cutting` AND `risk_regime ≠ risk_off` |

**Crisis mode (the anti-fragile playbook):**

When `crisis_flag = true`, gates **invert** — they become floors, not ceilings:

| Normal mode | Crisis mode |
|---|---|
| VIX > 25 BLOCKS USD adds | VIX > 40 + HY-OAS > 800bps **MANDATES** forced DCA on Tier-1 names (≤ 0.5% book / week for 4 weeks) |
| Crypto F&G > 75 BLOCKS BTC | Crypto F&G < 10 **MANDATES** DCA escalation ($200–500 / tranche, 2-week cadence) |
| Tilt cooldown overrides BUYs | Tilt cooldown waived for pre-committed crisis-DCA schedule (still required for new-name BUYs) |

**Output of Step 7.5 (single JSON block, surfaced in TL;DR risk bullet if non-neutral):**

```json
{
  "risk_regime": "...",
  "rates_regime": {
    "fed": "hiking | holding-hawkish | holding-neutral | holding-dovish | cutting",
    "bi":  "hiking | holding-hawkish | holding-neutral | holding-dovish | cutting",
    "mas": "tightening_neer | hold_neer | easing_neer"
  },
  "inflation_regime": {
    "us": "accelerating | sticky | cooling",
    "id": "accelerating | sticky | cooling",
    "sg": "accelerating | sticky | cooling"
  },
  "current_rates_snapshot": {
    "fed_funds_target": "x.xx–y.yy%",
    "us_3m_tbill": 0.0,
    "us_10y": 0.0,
    "bi_rate": 0.0,
    "indogb_10y": 0.0,
    "sora_3m": 0.0,
    "sgs_10y": 0.0
  },
  "next_release_calendar": {
    "us_cpi": "YYYY-MM-DD",
    "fomc": "YYYY-MM-DD",
    "bi_rdg": "YYYY-MM-DD",
    "mas_mps": "YYYY-MM-DD"
  },
  "crisis_flag": false,
  "z_scores": {"dxy": 0.0, "vix": 0.0, "hy_oas": 0.0, "2s10s": 0.0, "ovx": 0.0, "usdidr": 0.0},
  "active_gates_used": "relative | static",
  "regime_drift_warning": "yes/no — flipped vs last 7 sessions"
}
```

If `regime_drift_warning = yes`, mention in TL;DR — a regime flip without acknowledgment is the macro-flip-flop failure mode Step 1.5 was designed to catch.

### Step 8 — Micro research (with multi-lens framework)

**Auto-trigger rules — run without waiting for Yu to ask:**

| Condition | Sub-skill / lens to invoke | What it produces |
|---|---|---|
| Any position with **DD ≥ 18%** from cost | `equity-research:thesis` | Is original thesis still intact? Hold/cut verdict. (Lowered from 20% to catch DCII-like "-19%" cliff cases.) |
| Any position with **DD between 12% and 18%** | Pre-flag only — no full thesis, but mark `APPROACHING_TRIGGER` for the next session | Avoid surprise jumps from "clean" to "broken" |
| Any position breaking 52w high + IRR > 25% | `equity-research:model-update` + Tier 0 evaluation | Asymmetric — adds-on-strength path matches Yu's winners pattern |
| Any position with **earnings within 14 days** | `equity-research:earnings-preview` | Beat/miss scenarios, key metrics to watch, P&L impact |
| Any position **not yet deeply researched** (IREN, DCII, SOUN) | `equity-research:initiating-coverage` | Full DCF, competitive moat, 12M target price |
| New position detected in tracker | `equity-research:initiating-coverage` | Always initiate on first appearance |
| Yu asks "should I buy more X" | `equity-research:model-update` | Update model with latest data, revise target |
| **Multi-year structural / 3+ yr hold** | **Aschenbrenner trendline lens** | Identify bottleneck input, write 3–5 yr exit triggers |
| **Geographic concentration / datacenter / AI infra** | **Kevin Xu geopolitics lens** | Moratorium tracker, jurisdictional risk, Asia-pivot beneficiaries |

**Aschenbrenner trendline lens (when applied):**
1. What 3–5 yr trendline does this name ride?
2. What is the most constrained input on that curve?
3. Is this name the constraint, or does it depend on the constraint?
4. Pre-commit exit triggers tied to thesis break (not price)
5. Hold horizon = curve duration, not calendar

**Kevin Xu geopolitics lens (when applied):**
1. Where does this asset operate / depend on operating?
2. Are there moratoriums, sanctions, or regulatory blocks emerging?
3. Does the trade benefit from US→Asia capex migration?
4. Cross-reference Interconnected Capital moratorium tracker

**Standard micro check (all top 10 positions):**
- Analyst consensus target vs current price
- Recent earnings/dividend/news
- Red flags (guidance cut, insider selling, regulatory hit)
- Flag: target < current price → SELL signal from consensus
- **"Late-cycle entry" check:** has the name run >50% in last 12 months? Flag and require DCA pace, no lump sum.

**Per-position thesis cards (auto-generated for DD ≥ 18%):**
Using `equity-research:thesis` format — one card per flagged position showing:
- Original thesis (why bought)
- Current thesis status (intact / weakening / broken)
- Catalyst needed to recover
- Recommended action

**Current auto-trigger list (May 2026):**
- COIN.JK (-70%) → thesis check ← BROKEN, exit eval
- BUMI.JK (-50%) → thesis check ← BROKEN + mineral tax hit
- CDIA.JK (-41%) → thesis check ← weakening
- PANI.JK (-37%) → thesis check
- PYPL (-34%) → thesis check ← BROKEN, mgmt-guided decline
- SOUN (-27%) → thesis check ← weakening
- META (earnings ~Q2) → earnings-preview when within 14 days
- NVO (earnings ~Q2) → earnings-preview when within 14 days
- DCII (-19%) → Aschenbrenner + Xu lens (top conviction IDX)
- VRT, CEG, PWR (NEW potential adds) → Aschenbrenner lens for sizing

### Step 9 — Drift analysis

Current vs target per overall category AND per currency bucket. Flag drift > ±band.

### Step 10 — Risk metrics (statistical-rigor hardened)

**Pre-conditions (fail-closed):**
1. Count observations N from `Snapshots` sheet for the trailing 12 months.
2. **N ≥ 60** required for Sharpe, Sortino, VaR, Sortino. If `N < 60` → output `"insufficient_sample: N=<n>, need ≥60"` and skip the metric (do NOT compute with low N).
3. **Declare frequency explicitly** in the report (daily / weekly / monthly). Annualize using the frequency-correct factor (√252 / √52 / √12) — never assume.
4. **Live risk-free rates per run** (replaces hardcoded 5.5/3.5/4.25%):
   - IDR rf = INDOGB 3M yield (WebSearch `"Indonesia 3-month government bond yield"`)
   - SGD rf = MAS 3M T-bill yield (WebSearch `"Singapore 3-month T-bill yield"`)
   - USD rf = US 3M T-bill yield (FMP `economics` or WebSearch)
   - Cache 24h with TTL field; fail-closed if pull fails AND cache stale.

**Metrics per currency bucket:**
- **Sharpe** = (annualized excess return − live rf) / annualized vol. Report with N + frequency + rf used as-of date.
- **Sortino** = excess return / downside vol (target = live rf, not zero).
- **Max drawdown** = peak-to-trough on the Snapshots series; report date range.
- **Concentration HHI** — flag > 0.25.
- **Portfolio VaR 95% 1-month** — **historical simulation** (not parametric) for any bucket containing Gold > 5% or Crypto > 2%. Fat-tail-aware. Parametric only allowed for pure FI/cash buckets.
- **Expected Shortfall (CVaR 95%)** — average loss in the worst 5% of historical 1-month returns. Mandatory for buckets where Gold + Crypto > 10%.

**Per position:**
- Drawdown since cost
- Annualized vol (with N + frequency disclosure)
- Position Sharpe (live rf, same frequency)
- **Tail-risk flag** — if position's worst trailing-30-day return < −2σ of its own history, mark `TAIL_HIT` for Step 12 cross-check.

**Report any metric with insufficient data as `n/a (N=<n>, need ≥60)` — never substitute a low-N estimate.**

### Step 11 — IPS compliance check + concentration auto-flag

Load `ips.json` (Drive state folder). Check:
- Allocation vs target bands
- Position concentration limits (max 25% bucket, max 10% total)
- Lock calendar (Makmur 100-wk positions)
- Watchlist triggers
- Single-name equity cap IDR (5%/name max)
- **Wedding fund progress** (SGD 0 May → 14K Aug → 20K Dec 2026)
- **Emergency fund floor** (SGD 10K liquid in Maribank SavePlus; revised from SGD 30K on 2026-05-13 due to SGD 15K credit-card bridge)

**Auto-flag (output explicit warning + recommendation):**
- Single fund/stock > 15% of total book
- Single sub-sleeve > 30% of bucket
- Top 3 positions > 50% of book
- Currently flagged: **PIMCO Income at 23% of total book** (Maribank + Endowus combined)

### Step 11.5 — Decision Journal & Tilt Gates (MANDATORY before Step 12)

The discipline ladder defends against drawdowns *after* they happen. This step defends against the behavioural pattern that produces them — late-cycle FOMO entries on hyped names (Yu's documented losers pattern: COIN, BUMI, PYPL, SOUN, BMNR, PANI, PTRO, GOTO, half-CDIA). All four gates below are checked **before** any BUY emits in Step 12.

**Gate A — Loss-Cooldown (24h)**
- IF any position closed/trimmed at a loss in last 24h **OR** total book drawdown > 5% in last 48h
- THEN all BUY recommendations downgraded to MONITOR. Output: `"Cooldown active until <timestamp>. No new BUYs. Use this window to re-read thesis cards, not act."`

**Gate B — Overtrading Frequency Cap**
- Read prior 2 sessions' action lists.
- IF a ticker appears in this session's BUY/SELL list AND appeared in either of the prior 2 sessions
- THEN require explicit `<reason_for_revisit>` field in the recommendation. Reject "still looks good" — must cite a new catalyst, price level, or thesis update since last call.

**Gate C — Hard FOMO Block (replaces soft "late-cycle entry" flag)**
- IF a candidate name has run > 30% in the last 90 days (close-to-close)
- THEN: lump-sum BUY is BLOCKED. Only path forward is a pre-committed DCA schedule:
  - Tranche size = ≤ 0.5% of total book per entry
  - Min 4 tranches, min 2 weeks apart
  - Schedule recorded in `decision-log.jsonl` before first tranche executes
- IF the same name has run > 50% in 90d: BLOCKED entirely, written into watch list with a "wait for -15% pullback" trigger.

**Gate D — Execution-time Decision Card (writes, doesn't just read)**
Every BUY/SELL/TRIM recommendation Step 12 emits MUST come with a decision card appended to `decision-log.jsonl` (Drive state folder):

```json
{
  "timestamp": "...",
  "ticker": "...",
  "action": "BUY | SELL | TRIM | HOLD",
  "tier": "1 | 2 | 3 | 4",
  "thesis_one_sentence": "...",
  "falsification_trigger": "what makes this thesis wrong (price level, fundamental, macro)",
  "max_position_size_pct_book": 0.0,
  "planned_hold_horizon_months": 0,
  "emotional_state_1to5": 0,
  "is_revisit": true,
  "reason_for_revisit": "...",
  "gate_status": {"cooldown": "pass", "overtrading": "pass", "fomo": "pass"},
  "preceded_by_loss_24h": false
}
```

Step 1.5 reads this log on next session (not just yesterday's recs) — closes the hindsight-bias loop.

**Mirror: Winner-Logging Ladder**
Loss-aversion is symmetric — un-managed winners get stranded. Pre-commit on the way up too:

| Move from cost | Pre-committed action |
| --- | --- |
| +30% | Log what worked in `decision-log.jsonl` (`win_thesis_validation` field). Do NOT trim yet. |
| +50% | Pre-commit a 20% trim if thesis hasn't expanded; if thesis has expanded, document the new TP. |
| +100% | Mandatory trim 25% to recover original cost basis. Let the rest run. |
| Any euphoria | Re-read losers pattern (Notes section). Do NOT add. |

**Output of Step 11.5:**
- Cooldown status (active / clear)
- List of tickers triggering overtrading cap
- List of tickers triggering FOMO block (with 90d run %)
- Today's required decision cards (one per Step 12 recommendation)
- Any winners triggering the mirror ladder

### Step 12 — Recommendations + mandatory cross-check + HARD GATES

For each currency bucket independently: BUY/SELL/HOLD/MONITOR.

Output format — **5-tier rebalance system (Tier 0 added for late-winner adds on strength):**

| Tier | Definition | Output requirement |
|---|---|---|
| **Tier 0 — ADD ON STRENGTH** | Existing winner, thesis still expanding, breaking out, IRR > 25%, position size < IPS cap | Trigger price (52w high break or +5% above prior consolidation) + tranche size (≤ 0.5% book) + max position cap |
| **Tier 1 — DOUBLE DOWN** | Multi-year structural conviction, scale aggressively (typically on weakness) | 3-yr thesis + DCA pace + exit triggers + discipline ladder |
| **Tier 2 — STRONG ADD** | Structural but secondary, add on weakness | DCA trigger conditions + position cap |
| **Tier 3 — HOLD** | Working position, no add no cut | None |
| **Tier 4 — TRIM/CUT** | Broken thesis / no moat / dilution risk / cleanup | Exit price + redeployment target |
| **NO-TRADE** | Signals conflict OR cooldown/freshness gate active OR low-edge regime | Output `"NO-TRADE: <reason>. Re-evaluate in <N> days."` Never invent action to fill the table. |

**Cross-check matrix (HARD GATES — no soft override):**

| If... | Then... |
|---|---|
| **Maribank SavePlus < SGD 10K** OR action would breach the SGD 10K floor | **HARD GATE: ALL adds BLOCKED across every bucket** — refund emergency floor first. Explicit opt-in required to override. (Floor revised 2026-05-13 from SGD 30K → SGD 10K because Yu carries an SGD 15K credit-card limit as bridge liquidity, treated bridge-only — never carries a balance month-over-month.) |
| **Wedding-ladder month-target unmet** (SGD 0 May → 14K Aug → 20K Dec 2026) | **HARD GATE: equity + crypto adds BLOCKED** — top up wedding sleeve first. |
| **Discipline-ladder savings-redirect proposed** (the -30% rung redirecting 50% of monthly savings) | **HARD GATE: only allowed if (a) emergency floor ≥ SGD 30K AND (b) wedding-ladder current month-target funded**. Otherwise downgrade to "stay-the-course DCA, no escalation." |
| **USD/IDR > 17,000** | **HARD GATE: IDR equity adds BLOCKED** (except structural single-tranche conviction names) |
| **USD/IDR > 17,500** | **HARD GATE: IDR equity TRIM signal** |
| **VIX > 25 + recession prob > 30%** | **HARD GATE: USD equity adds BLOCKED** for 7 days |
| **Crypto F&G > 75** | **HARD GATE: BTC adds BLOCKED** |
| Oil up + Fed hawkish | Do NOT add gold |
| Oil < $90 sustained | Gold add window OPEN |
| Fed dovish + oil stable | ADD gold, ADD SG REITs (CLR.SI) |
| Crypto F&G < 25 | DCA BTC $50-100 |
| Position IRR < blended RF | Flag for exit or reallocation |
| Thesis check = BROKEN | Recommend exit plan |
| **BUY-WINDOW: VIX > 30 + 1-day reversal candle (≥ +2% off intraday low)** | **USD opportunistic add WINDOW OPEN** — Tier 1/2 names only, ≤ 1% book per tranche, max 3 tranches |
| **BUY-WINDOW: USD/IDR spike > +1.5σ trailing 90d + IDX -15% intraday** | **IDR opportunistic tranche PERMITTED** (overrides USD/IDR > 17,000 block for THIS session only, single-tranche conviction names) — max 0.5% book |
| **BUY-WINDOW: BTC F&G ≤ 20 + 7-day RSI < 30** | **BTC DCA escalation OPEN** — double normal $50-100 to $100-200 / tranche |
| **BUY-WINDOW: HY-OAS > 700bps OR yield-curve un-inverts from > 60d inversion** | **Risk-on regime open** — equity-research:screen authorized to refill cash buckets aggressively |
| **Position breaking 52w high + thesis-card status = "expanding" + IRR > 25% + position < IPS cap** | **Tier 0 ADD-ON-STRENGTH eligible** (the only path to add to a winner without a drawdown excuse) |

**If recommendation requires gated action:**
- Output: "HARD GATE BLOCKED — [trigger condition]. User opt-in required to override."
- Do NOT silently bypass gates.

**equity-research:screen trigger:**
If any currency bucket has >3% cash above IPS target AND cross-check allows equity adds → invoke `equity-research:screen` with these filters:
- **USD bucket**: NASDAQ/NYSE, market cap > $5B, sector = AI infra (datacenter/power/cooling/semis) / healthcare / energy, analyst upside > 20%
- **SGD bucket**: SGX-listed, yield > 4%, REIT or blue-chip only
- **IDR bucket**: BLOCKED until USD/IDR < 17,000

**EM diversification rule:**
- Direct Indonesia exposure already exceeds 50% → DO NOT recommend MSCI EM as primary EM vehicle (28% China + 22% Taiwan + 18% India + 1.5% Indo = duplicates Indo + adds China geopolitical risk).
- Default EM diversifier = **India-specific ETF** (Amundi MSCI India equivalent on Endowus, or INDA via moomoo).
- Skip China-heavy EM unless macro flagged (China stimulus cycle signal).

### Step 13 — Final summary + $1M milestone tracker + stress test

**Deliver in this order (TL;DR + Trade Tickets first, always):**

0. **TL;DR (mandatory, top of report, max 3 bullets, max 25 words each):**
   - One bullet on portfolio status (total + delta + gap to $1M)
   - One bullet on the single most important action this session (with ticker + size + price)
   - One bullet on the single biggest active risk (gate tripped, thesis broken, freshness fail)
1. **Trade Tickets table (mandatory, immediately under TL;DR):** copy-paste-ready, one row per recommendation. Columns:

   | When | Bucket | Action | Ticker | Qty / Notional | Limit Price | Broker | Gate Status | Tier | Decision-card ID |
   |---|---|---|---|---|---|---|---|---|---|

   - `When` = `TODAY` / `THIS WEEK` / `THIS MONTH` (split, never just "soon")
   - `Bucket` = IDR / SGD / USD
   - `Action` = BUY / SELL / TRIM / DCA / HOLD
   - `Qty / Notional` = lots, units, or notional with currency
   - `Limit Price` = specific number, NOT "around X"
   - `Broker` = Makmur / Bibit / Maribank / Endowus / Stockbit / LongBridge / moomoo / Webull / GXS / OCBC
   - `Gate Status` = `PASS` or `OPT-IN REQUIRED: <reason>`
   - `Tier` = 1/2/3/4 from Step 12 four-tier system
   - `Decision-card ID` = the UUID/index from `decision-log.jsonl` (Step 11.5 Gate D)

2. Portfolio total (IDR + SGD + USD equivalent)
3. Delta vs last snapshot
4. **$1M milestone tracker** (see below — mandatory every run)
5. **Stress test** for any sleeve targeted to >10% of book (mandatory)
6. **Discipline ladder** for any new sleeve build (mandatory)
7. Top 3 watch items (not actions — things that *might* become actions next week)
8. What to keep untouched + why
9. Upcoming catalysts (dates) — **MUST include: next US CPI release (BLS), next FOMC date, next BI Rapat Dewan Gubernur (RDG), next MAS Monetary Policy Statement, next Indonesia CPI (BPS), next Singapore CPI (SingStat), earnings dates for held US + SG single-names, ex-dividend dates for PIMCO + S-REITs + STI banks**
10. Sources with URLs

**Rule:** if there are no recommendations this session, the Trade Tickets table contains a single row `NO ACTION | — | HOLD | — | — | — | — | PASS | 3 | —` and the TL;DR's action bullet says `"No trades — cooldown / gates / no edge."` Never omit the table.

**$1M Milestone Tracker (mandatory — show every single run):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$1M MILESTONE TRACKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current:      $___K  (IDR ___B)
Target:       $1,000K
Gap:          $___K  (___× needed)

Scenarios (with verified savings rate of SGD ___K/month):
  Conservative (8% pa):   __ years  (____-__-__)
  Moderate    (12% pa):   __ years  (____-__-__)
  Aggressive  (15% pa):   __ years  (____-__-__)

Sensitivity to savings bump (SGD +1K/month):
  Conservative: __ months saved
  Moderate:    __ months saved

Biggest lever this week:
  → [specific action that most accelerates the timeline]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Compute using: FV = PV×(1+r)^n + PMT×((1+r)^n - 1)/r

**Stress Test (mandatory for any sleeve > 10% of book):**

```
Sleeve: [name]
Current: [IDR/SGD/USD]
Target:  [IDR/SGD/USD]

Drawdown impact on TOTAL BOOK:
  -10%:  -IDR ___M (-_._% of book)
  -25%:  -IDR ___M (-_._% of book)
  -40%:  -IDR ___M (-_._% of book)

Hedge sleeves (anti-correlated):
  Gold (___% of book)         — typically +5–20% in equity crash
  Bibit FR Bonds (___% of book) — typically +5–10% in rate cuts
  Cash/MM (___% of book)       — zero loss
  
Net portfolio impact at -25% sleeve drawdown:
  After hedges: ___% of total book
```

**Discipline Ladder (mandatory for any new sleeve build):**

```
| Drawdown   | Pre-committed action                                           |
| ---------- | -------------------------------------------------------------- |
| -10%       | Continue DCA at planned size                                   |
| -20%       | Continue + add 1 extra tranche                                 |
| -30%       | Redirect 50% of monthly savings into this sleeve for 3 months — **ONLY if emergency floor ≥ SGD 10K AND wedding-ladder current month-target funded**. Else stay-the-course DCA. |
| -40%       | Trim hedge sleeve to opportunistic add                         |
| Any panic  | DO NOT SELL. Re-read this checklist.                           |
```

**Artifacts written at end of run:**
- `portfolio-analysis-<YYYY-MM-DD>.md` → sandbox working dir (the deliverable; surface to user)
- `last_snapshot.json` → **Drive state folder** (overwrite — persistent fallback for next run's Step 0)
- any mutated sidecars (`outcomes.jsonl`, `decision-log.jsonl`, `current_state.json`, `thesis_cards.json`, …) → **Drive state folder**, per the Step 0.5 write-back rule

End with: *"Informational analysis, not financial advice."*

---

## Equity Research Integration (auto-triggered, not manual)

| Condition | Skill / lens invoked | Frequency |
|---|---|---|
| DD > 20% on any position | `equity-research:thesis` | Every full run |
| Earnings within 14 days | `equity-research:earnings-preview` | Every full run |
| New position in tracker | `equity-research:initiating-coverage` | On first detection |
| Multi-year structural hold | **Aschenbrenner lens** | On structural recommendation |
| Geographic / datacenter / AI infra | **Kevin Xu lens** | On Asia-pivot or moratorium-relevant trade |
| "Deep dive on X" | `equity-research:initiating-coverage` | On demand |
| "Ideas for new names" / cash > target | `equity-research:screen` | On demand / auto |
| "What's moving" | `equity-research:morning-note` | On demand |
| "Sector check" | `equity-research:sector` | On demand |
| "Update model for X" | `equity-research:model-update` | On demand |
| "Catalysts this week" | `equity-research:catalysts` | On demand |
| "Should I cut X" | thesis-break check + position-quality matrix (auto) | On demand |
| "Should I double down" | 4-tier system + DCA schedule + discipline ladder (auto) | On demand |
| "How to rebalance Y bucket" | drift analysis + FX gate + execution order with limit prices (auto) | On demand |
| "Explain investor Z" | Add lens to research toolkit + apply to current book | On demand |

**Position context always applied before any equity-research sub-skill:**
- Cost basis (underwater or profit?)
- Position size vs IPS limit
- Currency bucket + IPS phase
- Singapore: no CGT
- $1M acceleration impact
- Yu's "buyer not trader" pattern (DCA bias, structural-only)

---

## MCP Data Source Strategy

Yu has multiple MCPs connected. Use the **right MCP for the right data**, in priority order: FMP MCP (free + always-on) → LSEG (auth, deep fundamentals) → S&P Global Capital IQ via Kensho (auth, deal/M&A) → Google Drive (Tracker) → Claude in Chrome (Yahoo / Bareksa / xe.com fallback) → WebSearch (catch-all).

### 1. FMP MCP — primary live-data source (free-tier scope expanded)

| Endpoint | Use for | Notes |
|---|---|---|
| `commodity → commodities-quote` (`GCUSD`, `SIUSD`, `CLUSD` for WTI, `BZUSD` for Brent) | Gold, silver, oil spot prices — Topic 4 + Topic 3 | Always works on free tier |
| `crypto → cryptocurrency-quote-short` (`BTCUSD`, `ETHUSD`) | Crypto Topic 8 | Free tier |
| `quote → batch-quote-short` (`["META","PYPL","SOFI",...]`) | US single-name verification | **BLOCKED on Yu's FMP plan (free tier)** as of 2026-05-13 — error: `ACCESS DENIED: requires Premium/Ultimate/Enterprise`. Do NOT call this endpoint; go straight to Yahoo Chrome JS fallback. Reassess if Yu upgrades FMP plan. |
| `calendar` | **Ex-div + earnings + economic + IPO calendars** — feeds Step 1.6 #3 (ex-div sweep) + Step 8 auto-trigger (earnings within 14d) + Step 13 catalysts | Endpoints: `dividends-calendar`, `earnings-calendar`, `economic-calendar`, `ipo-calendar` |
| `analyst` | **Consensus target price + recommendation + estimates** — Step 8 standard micro check ("target < current price → SELL signal from consensus") | Endpoints: `price-target-consensus`, `analyst-estimates`, `grade` |
| `news` | **Company news + market news + press releases** — Step 1.6 #4 (M&A / delisting scrape), Step 8 red-flag check | Endpoints: `stock-news`, `general-news`, `crypto-news`, `forex-news`, `press-releases` |
| `economics` | **Macro indicators** — CPI, GDP, unemployment, retail sales, ISM, treasury yields | Use FIRST for Topic 0 (CPI) + Topic 1 (US rates) before falling back to FRED WebSearch |
| `insiderTrades` | **Insider buy/sell signals** — Step 8 red-flag check on top 10 positions | Endpoints: `insider-trading` — flag large insider sells |
| `form13F` | **Institutional holdings** — track smart-money positioning on top conviction names (NVO, IREN, DCII when listed in ADR form) | Endpoint: `institutional-holdings` |
| `senate` | **US Senate / House trading disclosures** — political-flow signal on sectors (defense, energy, healthcare) | Endpoint: `senate-trading` |
| `earningsTranscript` | **Deep-dive sub-skills** — used by `equity-research:initiating-coverage` for thesis cards | Topical excerpts, search-by-keyword |
| `secFilings` | **8-K (material events), 10-K, 10-Q, proxy** — corp-action sweep + thesis card forensic | Endpoint: `sec-filings`, filter by form type |
| `statements` | **Income, balance sheet, cash flow** — DCF inputs, leverage check | Quarterly + annual |
| `technicalIndicators` | **RSI, MACD, MA crossovers** — feeds Step 12 BUY-WINDOWs (`BTC F&G ≤ 20 + 7-day RSI < 30`, `STI 200d MA breach + RSI < 30`) | Endpoint: `technical-indicators` — RSI period 7/14/30 |
| `marketPerformance` | **Sector rotation** — which sectors leading/lagging | Use to validate equity-research:screen sector tilts |
| `discountedCashFlow` | **Auto-DCF** — cross-check against own DCF in initiating-coverage | Quick sanity, not authoritative |
| `commitmentOfTraders` | **CFTC positioning** — gold, oil, BTC futures | Topic 3 + Topic 4 + Topic 8 — flag extreme net-long/short |
| `etfAndMutualFunds` | **ETF holdings + flows** — useful for understanding IAU/GLDM/G3B/CLR composition | Endpoint: `etf-holdings` |
| `indexes` | **STI, S&P 500, Nikkei, JCI quotes** — Topic 2.5 (STI level) + Topic 7 | Free tier confirmed for major indexes |
| `marketHours` | **Per-currency market-open calendar** — Step 1.6 #7 | Already required by Step 1.6 |
| `chart` | **Historical OHLC** — z-score computation in Step 7.5 regime classifier | 60-90d windows |
| `directory` | Symbol lookup | Use sparingly |
| `company` | Company profile metadata | Use sparingly |
| `quote → full-forex-quotes` | USD/IDR, SGD/IDR | **Blocked on free tier** — Yahoo / xe.com fallback for forex |

### 2. LSEG MCP (Refinitiv) — institutional-only, SKIP for personal portfolio

The MCP plugin is installed and free, BUT the underlying Refinitiv Workspace account is **institutional-priced (~USD 22K–30K+ per year per seat)**. Yu's book size (USD 242K, SGD 2K/month savings) makes this categorically wrong — it would be ~9% of book annually for the seat alone.

**Default: do not call `authenticate` for LSEG.** Skip entirely. Use FMP + Yahoo + WebSearch for everything LSEG would have covered.

**Only revisit if:**
- Yu gains LSEG access through an employer seat at zero personal cost, OR
- Book grows past USD 5M+ where institutional data marginal-utility becomes justifiable

LSEG-prefixed sub-skills (`lseg:macro-rates-monitor`, `lseg:bond-relative-value`, `lseg:fixed-income-portfolio`, `lseg:fx-carry-trade`, `lseg:equity-research`) require the auth and should NOT be auto-triggered until that condition is met.

### 3. S&P Global / Kensho Capital IQ MCP — institutional-only, SKIP

Same story as LSEG. Capital IQ Pro is **~USD 15K–22K+ per year per seat**. Plugin is free, underlying account is not.

**Default: do not call `authenticate` for S&P Global.** Skip entirely.

Sub-skills (`sp-global:tear-sheet`, `sp-global:funding-digest`, `sp-global:earnings-preview-beta`) require auth; do not auto-trigger.

### 4. Google Drive MCP — Tracker source of truth + portfolio state

- `search_files` + `read_file_content` for Tracker workbook
- `download_file_content` (exportMimeType `xlsx`) to load into openpyxl
- Used in Step 1 (Read Tracker) and Step 0 (Snapshots delta)
- **Also the home of all skill state** — the `Portfolio-Analyzer-State` folder (ID `1KIQdf-Z027GGeqZ_zDHf0LOK_MJLK8Z8`) holds every sidecar (Step 0.5). `create_file` (with `contentMimeType: application/json`, `disableConversionToGoogleType: true`) bootstraps/writes them. **This connector is the skill's one hard dependency** — if it is not connected, Step 0.5 hard-fails.

### 5. Claude in Chrome MCP — browser fallback

When FMP, LSEG, and S&P Global all fail or are gated, fall back to browser scraping:
- Yahoo Finance for SGX `.SI`, IDX `.JK`, US ETFs (IAU, GLDM, SLV, etc.), small-cap US (IREN, BMNR, etc.) — primary source per current skill rules
- Bareksa scrape for IDR mutual fund NAVs + distributions (Step 3) — still mandatory in full run
- xe.com for FX (USD/IDR, SGD/IDR) when FMP forex is blocked
- mas.gov.sg, bi.go.id, bls.gov, fred.stlouisfed.org for macro releases
- Used by `mcp__Claude_in_Chrome__navigate` + `read_page` + `javascript_tool` for SPA-heavy sites

### 6. WebSearch — catch-all

For everything else: news headlines, geopolitical scans, central-bank statements that aren't on FMP `news`, BPS Indonesia CPI release (BPS site isn't easy to scrape), URA quarterly property data, MAS REIT rule changes.

### Cost discipline

The Step 5 execution contract has token + time budgets per step. Most FMP calls are 1–3K tokens each. Stack them in **parallel** (single message, multiple `mcp__3b437285-...` tool calls) where possible — the workflow contract assumes parallelism for the price-pull stage. Sequential pulls eat the budget fast.

### Quick-run vs full-run MCP usage

| Mode | FMP | LSEG | S&P | Chrome | WebSearch |
|---|---|---|---|---|---|
| Quick run | always | **SKIP** (cost) | **SKIP** (cost) | only if a quote unverified | only for unique catalysts |
| Full run | always | **SKIP** (cost) | **SKIP** (cost) | required (Bareksa + Yahoo for SGX/IDX/US single names) | required for macro releases |
| Reconcile-only | minimal (FX + gold) | **SKIP** | **SKIP** | required (Bareksa) | minimal |
| Single-name | always | **SKIP** | **SKIP** | required fallback | minimal |

**Why "SKIP" for LSEG / S&P across all modes:** these MCPs require institutional seats (~USD 15K–30K+/yr/seat). Not cost-justified for personal-portfolio book size. Re-enable only if Yu gains seat access via employer at zero personal cost, or book grows past USD 5M.

---

## On-demand modes

- **Full run** (Tracker uploaded): Steps 0-13, ~20-90 min
- **Quick run** ("quick analysis"): Skip Bareksa, use cached reconciliation
- **Reconcile only** ("reconcile funds"): Steps 0, 1, 3, 5, 6, 13
- **Risk only** ("check risk"): Steps 0, 1, 4, 10, 11, 13
- **Single-name** ("should I sell X"): Rules 1-4, auto-invoke equity-research:thesis, position context
- **Screen mode** ("find new stocks"): equity-research:screen with bucket filters + cross-check gating
- **$1M mode** ("how do I hit $1M"): Milestone tracker + scenario modeling + biggest-lever analysis
- **Aschenbrenner mode** ("structural picks" / "what to double down"): trendline → bottleneck → 3-yr hold framework on current book
- **Xu mode** ("geopolitics check"): Moratorium tracker review + Asia-pivot beneficiaries
- **Stress mode** ("what if [sleeve] drops"): Stress test + discipline ladder for specific sleeve

---

## Notes that matter

- IDX: 1 lot = 100 shares
- Makmur NAV updates ~6-7 AM WIB
- PIMCO: TWO rows in `SGStockEvent` — `Notes=Maribank` (Admin 1.45% TER) + `Notes=Endowus` (Institutional 0.55% TER). Track separately. **Combined ~20-23% of book → concentration flag.**
- Gold ETFs (GLDM, IAU, IAUM, GLS.SI) and SLV → "Gold", not "Equity". Detection: `TYPE=G`/`Type=G` in US sheets, `Type=G` in SGLongbridge/SGStockEvent, plus ticker match as fallback.
- **US holdings are split per broker**: Moomoo, Longbridge, Webull each have their own sheet. Combine all three for total US exposure. Use the `TYPE`/`Type` column (all three US sheets now use it — `IsGold` was renamed to `Type` in v5.5) to classify Stock vs Gold vs Crypto.
- Weekend prices = last trading day close
- Tracker uses GOOGLEFINANCE — only refreshes when opened in Google Sheets. The `Snapshots` sheet is the durable history (independent of GOOGLEFINANCE refresh state).
- CLR.SI = Lion-Phillip S-REIT ETF (not Lion-OCBC)
- G3B.SI is now labeled **Amova Singapore STI ETF** (was Nikko AM STI ETF — rebranded)
- Bibit Bonds IDR 154.8M = SBN + FR series, HTM, coupons to cash wallet
- IDR: no retail CGT
- SLV trim trigger: $80/oz (currently $73.01 — monitor for $76/$80/$85 ladder)
- MSCI freeze: BREN/DSSA removed May 4 — IDX structural headwind
- Mineral tax: export duty 5-11% on coal/nickel pending ESDM finalization — BUMI direct hit
- **Maribank Saveplus emergency floor: SGD 10K** — never trim below this. Revised down from SGD 30K on 2026-05-13: Yu carries an SGD 15K credit-card limit as **bridge liquidity only** (used for true emergencies, full balance repaid each cycle, never carries month-over-month — CC is a fire extinguisher not a soft floor extension). If CC ever rolls a balance, revisit the floor immediately.
- **Wedding period: now → Jan 2027.** Capital preservation > growth during this window
- **Valas is a new top-level category** — FX cash held outside investment products. Don't roll into Cash bucket; report separately per IPS.
- **Two history sheets, different uses:** `SnapshotLog` = rolled-up per account+category in IDR; `Snapshots` = per label with native currency preserved. Use `Snapshots` for currency-bucket return calcs.
- **Yu's losers pattern: COIN, BUMI, PYPL, SOUN, BMNR, PANI, PTRO, GOTO, half-CDIA all share — late-cycle entries on no-moat / structurally declining names.** Do not repeat the pattern when recommending new buys.
- **Yu's winners pattern: gold, FI funds, NVO, IREN, structural compounders bought DCA-early.** Bias new recommendations to this shape.

---

## Sidecars + Outcomes Log (maintainability spec)

All volatile state lives in versioned sidecar files in the **Google Drive state folder**, not in the skill body and not "alongside SKILL.md" (the skill directory is read-only — it cannot hold state). Each file has a `_meta` block with `schema`, `last_updated`, and a `note`.

**State folder:** `Portfolio-Analyzer-State` — Drive folder ID `1KIQdf-Z027GGeqZ_zDHf0LOK_MJLK8Z8`, in Yu's My Drive. Accessed via the Google Drive connector. If the connector is not connected the skill hard-fails at Step 0.5 — it is the one true dependency.

**Connector call conventions (important):**
- **List folder contents** — `search_files` with `query: "'<folderId>' in parents"`.
- **Read a sidecar** — `download_file_content` (returns base64 → decode to UTF-8 → `json.loads`). Do **not** use `read_file_content` — it rejects the `application/json` mime type.
- **Create / overwrite a sidecar** — `create_file` with `parentId` = state folder, `textContent` = the JSON/JSONL string, `contentMimeType: "application/json"` (or `application/jsonl`), `disableConversionToGoogleType: true`. To overwrite, create the new version and treat the latest by `modifiedTime` as current (the connector has no in-place edit).
- Sidecar file IDs from the v5.6.0 bootstrap (2026-05-14): `ips.json` `12jffkvSJOicrakF1jDMFa2AES_ieJRnl`, `fund_registry.json` `1qdHpHbEzj9kx_Q35ZrE2qZpK1ayjhaVg`, `ticker_history.json` `1-uVWayvtIR2xryf2KN_RUjD1M9HEAdev`, `last_snapshot.json` `18duzy1liP-ya3mpBDIr9WfjAUP47AxY0`, `current_state.json` `12XNN0XzjQ4h5IbmywRMZTJVbxPem8RLS`, `watchlist.json` `1FFpg__-yZsZoB9gX7-DmVF4Tdg6XIAjt`, `thesis_cards.json` `1AeWXB-F3racIl2yXs4XE9hZWVXsvPvGF`, `decision-log.jsonl` `1w9WCXHvbFIdKOW6Xm1VjVbleZEajoJDD`, `outcomes.jsonl` `17IGK_IwwLscvMB8G9y3kKpTKX5ec4ceQ`. Re-resolve by name each run in case files were re-created.

### Sidecar files (all live in the Drive state folder)

| File | Purpose | Stale threshold |
|---|---|---|
| `ips.json` | IPS phase, target allocation, bands, currency-bucket targets, position caps, lock calendar, wedding-ladder, emergency floor, monthly savings, $1M target | 90 days |
| `fund_registry.json` | Bareksa slugs + Yahoo tickers per IDR fund | 30 days |
| `ticker_history.json` | Rebrand/ISIN-swap history (e.g. G3B Nikko AM → Amova) | 14 days |
| `last_snapshot.json` | Fallback portfolio snapshot if Tracker `Snapshots` sheet unavailable | 7 days |
| `current_state.json` | Live flags (PIMCO concentration %, mineral-tax status, MSCI freeze status, SLV trim level) | 14 days |
| `watchlist.json` | Candidate names + entry triggers | 30 days |
| `thesis_cards.json` | Per-position thesis cards (auto-managed from equity-research:thesis) | 30 days |
| `decision-log.jsonl` | Append-only execution-time decision cards (from Step 11.5 Gate D) | n/a (append-only) |
| `outcomes.jsonl` | Append-only outcomes log — track skill accuracy | n/a |

Schema is carried inline in each file's `_meta.schema` name + structure; there are no separate `schemas/*.schema.json` files. Validate structurally (required keys present, types sane), not against an external schema file.

### Bootstrap + drift check (mandatory — Step 0.5, self-healing)

```
ensure Drive connector reachable        → else HARD-FAIL
ensure state folder reachable/created   → else create it, note new ID
FOR each sidecar in the table above:
  IF missing        → create from embedded default template; log BOOTSTRAPPED; continue
  IF unparseable / structurally corrupt → HARD-FAIL "Schema drift: <file> — <diff>"
  IF last_updated > stale_threshold     → WARN + flag in TL;DR risk bullet
  IF template _todo fields still unfilled → flag in TL;DR "setup needed: <file>"
END
```

**Absence is healed, not fatal.** Only connector-unreachable or corrupt-file conditions hard-fail. A freshly bootstrapped run is valid but flags its `_todo` gaps.

### Bootstrap default templates

When a file is missing, create it with this minimal valid content (the v5.6.0 bootstrap created these on 2026-05-14 — this section is the regeneration spec):
- `ips.json` — `_meta` + `phase`, `risk_profile`, `horizon_years`, `base_currency`, `domicile`, `monthly_savings` {amount, currency, last_confirmed}, `milestone` {target_usd: 1000000}, `emergency_floor` {amount: 10000, currency: SGD}, `target_allocation` {current, growth_phase, bands — from the Target Allocation section of this skill}, `currency_buckets` {IDR/SGD/USD targets}, `rules`, and `_todo`-marked `position_caps` / `lock_calendar` / `wedding_ladder`.
- `fund_registry.json` — `_meta` + `funds: []` (each {name, source, bareksa_slug: null, yahoo_ticker: null}), `_todo` to fill slugs.
- `ticker_history.json` — `_meta` + `rebrands: [{ticker:"G3B.SI", from:"Nikko AM Singapore STI ETF", to:"Amova Singapore STI ETF", isin_changed:false}]`.
- `last_snapshot.json` — `_meta` + `snapshot: null`.
- `current_state.json` — `_meta` + `flags: {pimco_concentration_pct:null, mineral_tax_status:null, msci_freeze_status:null, slv_trim_level:null}`.
- `watchlist.json` — `_meta` + `candidates: []`.
- `thesis_cards.json` — `_meta` + `cards: []`.
- `decision-log.jsonl` / `outcomes.jsonl` — one `_meta` line, then append-only. The reader ignores any line whose object has a `_meta` key.

### Outcomes log (`outcomes.jsonl`)

Append one line per BUY/SELL/TRIM recommendation Step 12 emits. Used to measure skill accuracy over time.

```json
{
  "timestamp": "2026-05-13T17:00:00Z",
  "skill_version": "5.0.0",
  "decision_card_id": "<uuid>",
  "ticker": "DCII",
  "action": "BUY",
  "tier": 1,
  "size_pct_book": 0.5,
  "entry_price": 1010,
  "thesis_one_sentence": "Indonesia datacenter buildout — power-constrained, structural compounder",
  "falsification_trigger": "thesis broken if Indonesia power capacity policy reverses OR price > 2× cost without earnings catch-up",
  "horizon_months": 36,
  "review_30d_price": null,
  "review_30d_pct": null,
  "review_90d_price": null,
  "review_90d_pct": null,
  "review_180d_price": null,
  "review_180d_pct": null,
  "outcome_label": null,
  "outcome_note": null
}
```

At the start of every session, scan `outcomes.jsonl` for entries where `timestamp + 30d/90d/180d ≤ today` and `review_*` is null. Fill them in. Compute hit-rate per tier + per action. Surface in TL;DR if hit-rate drifts > 1σ from rolling baseline — the skill itself may be degrading.

### Version bump rule

Bump `version` in front matter (semver) on every meaningful change:
- **Major** (X.0.0): workflow restructure, new mandatory step, breaking sidecar schema change
- **Minor** (5.X.0): new gate, new lens, new sub-skill auto-trigger, new sidecar
- **Patch** (5.0.X): typo, threshold tweak, note addition

Update the Changelog section at the top of this file with every bump. Without the bump, `outcomes.jsonl` cannot attribute hit-rate to the right skill version.
