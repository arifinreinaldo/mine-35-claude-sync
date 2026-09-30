---
name: saturday-action
description: Yu's weekly Saturday portfolio review routine — 30-minute structured check covering macro tape, portfolio drift, calendar look-ahead, decision queue, and logging. Use whenever Yu says "saturday review", "weekly review", "weekly check", "saturday action", "what's the next action this week", "weekly routine", or asks for the periodic portfolio status update. Outputs a Markdown checklist with current readings against IPS triggers, the next-week action queue, and a one-line log entry. Always runs against the live tracker (refresh first via yu-portfolio-analyzer or Google Sheet sync). Monthly extension fires on the last Saturday of the month with extra reconciliation tasks. Aligned with Yu's phased IPS (Phase 1 wedding-prep through Jan 2027, Phase 2 wife-arriving, Phase 3 steady-state).
---

# Saturday Action — Yu's Weekly Portfolio Routine (v2 — upgraded May 2026)

Run every Saturday morning, 09:00 SGT, ~30 minutes. Markets closed → no reactive trading; review and queue next week's actions.

## Yu's context (always-applied)

- Domicile: Singapore (no CGT)
- Base currency: IDR
- Buckets: IDR / SGD / USD — no cross-currency rebalancing
- **Life events (current cycle)**: wedding Jan 2027 in Indonesia (SGD 20k portion), wife relocating to SG mid-2027 (Data Engineer, LTVP→PR, SGD 10k savings), assumed 12-month worst-case unemployment buffer
- **Active IPS phase**: depends on date
  - **Phase 1** (now → Jan 2027): wedding prep
  - **Phase 2** (Jan 2027 → wife employed): wife arriving / single-income bridge
  - **Phase 3** (wife employed onwards): steady state
- Communication: concise, direct, structured — no fluff

## Active IPS targets by phase

| Class | Phase 1 | Phase 2 | Phase 3 |
|---|---|---|---|
| FI + Bonds | 35% ±5 | 35% ±5 | 35% ±5 |
| Equity | 25% ±5 | 20% ±5 | 27% ±5 |
| Gold | 15% ±3 | 15% ±3 | 15% ±3 |
| Cash/MM | 17% ±3 | 22% ±3 | 15% ±3 |
| Crypto | 3% ±2 | 3% ±2 | 3% ±2 |
| Valas | 5% ±2 | 5% ±2 | 5% ±2 |

Wedding sinking fund (SGD 20k) is segregated from Cash allocation %.
Concentration limits: max 10% single-name, max 25% per bucket, max 5% per IDX equity.
Lock-in rule: no new lock-ups > 6 months until at least Q3 2027.
Emergency fund floor: SGD 30k in pure liquid (Maribank, OCBC, Endowus Cash Smart, GXS).

---

## The 5 blocks — in order

### Block 1 — Macro tape (5 min)

**ALWAYS start by calling these FMP MCP tools first — before any web search:**

| # | FMP Tool Call | What it gives |
|---|---|---|
| 1 | `commodity → commodities-quote → GCUSD` | Gold futures live price + day change |
| 2 | `commodity → commodities-quote → SIUSD` | Silver futures live price (SLV proxy) |
| 3 | `crypto → cryptocurrency-quote → BTCUSD` | BTC live price + 24h change |
| 4 | `quote → quote → META` | META price vs cost $739 |
| 5 | `quote → quote → PYPL` | PYPL price vs cost $69 |
| 6 | `quote → quote → SOFI` | SOFI price vs cost $18.98 |

Then web-search for the remainder (IDR/SGD forex, VIX, oil, Indo news).

| Check | Source | Threshold |
|---|---|---|
| Gold spot $/oz | **FMP: GCUSD** ✅ free | < $4,500 = add; > $5,200 = pause |
| Silver $/oz | **FMP: SIUSD** ✅ free | Track vs SLV cost $78.06 |
| BTC | **FMP: BTCUSD** ✅ free | F&G < 25 = DCA window |
| META / PYPL / SOFI | **FMP: quote** ✅ free | Track vs cost basis weekly |
| USD/IDR | xe.com / Bloomberg | > 17,400 = stress; < 17,000 = relief |
| SGD/IDR | Same | Trend direction WoW |
| Brent oil | TradingEconomics / Bloomberg | < $90 = gold add window; > $115 = freeze |
| S&P 500 + VIX | Yahoo Finance | VIX > 25 = freeze all new adds |
| BTC F&G index | alternative.me/crypto/fear-and-greed-index | < 25 = DCA trigger |
| Indo 10Y yield | TradingEconomics | > 7% = SBN entry; < 6.5% = pause |
| 1 Indonesian news | detik.com / kompas | Anything market-moving |
| 1 Hormuz / Iran headline | Reuters / Al Jazeera | Ceasefire confirmed? Re-escalation? |
| 1 Fed/Warsh signal | Bloomberg | Tone shift from new chair |
| Indonesia mineral tax | ESDM / ANTARA | Export duty 5–11% — finalized? |
| MSCI Indonesia status | IDNFinancials / heygotrade.com | Any freeze lift? New deletions? |

### Block 2 — Portfolio health (10 min)

Refresh the live tracker first (Google Sheet via Drive sync or `yu-portfolio-analyzer` skill).

**If Morningstar MCP connected:** pull current NAV for top 5 IDR mutual funds and compare vs tracker. Replaces Bareksa scrape.

| Check | Threshold | Action if breached |
|---|---|---|
| Total book vs last Saturday | -3% week | Investigate which sleeve drove it |
| IPS drift (FI/Eq/Gold/Cash/Crypto/Valas) | All within band? | Note breaches, queue rebalance |
| PIMCO % of book | Trending toward 18% then 10%? | Continue migration |
| Top-3 gainers WoW | — | Note for record |
| Top-3 losers WoW | -10%+ on week | Investigate single name |
| New position with DD > 30% | — | Decision: hold/cut (COIN -70%, BUMI -50% standing flags) |
| **BUMI mineral tax impact** | Any new ESDM announcement? | Execute exit decision if duty finalized |
| Wedding sinking fund progress | Target curve: 0 May → 14k Aug → 20k Dec 2026 | On-track? |
| Emergency fund | ≥ SGD 30k floor | Below = pause investments |
| Endowus PIMCO auto-buy | Verify still off | If on, disable |
| **FMP fundamentals check** (if connected) | Pull EPS/revenue for META, NVO, IREN | Flag any revision vs consensus |

### Block 3 — Calendar look-ahead (5 min)

**If FMP MCP connected:** run `earnings_calendar` for next 7 days filtered to your tickers. Replaces manual Yahoo calendar check.

| Check | Where |
|---|---|
| Earnings of any holdings next 7 days | **FMP MCP** → `earning_calendar` / Yahoo Finance |
| Analyst revisions for top positions | **FMP MCP** → `upgrades_downgrades` |
| FOMC / BI / MAS / data releases | forexfactory.com economic calendar |
| Distribution / ex-div dates | CLR (semi-annual), PIMCO (monthly), Trimegah FIP |
| Iran / geopolitical scheduled events | Reuters tracker |
| Wedding milestones / personal deadlines | Personal calendar |
| **Indonesia mineral tax ESDM meeting dates** | ESDM.go.id / ANTARA | Duty finalization expected Q2 2026 |
| **MSCI next review date** | msci.com | August 2026 — next potential freeze-lift |

### Block 4 — Decision queue (5 min)

| # | Trigger | Action |
|---|---|---|
| 1 | Endowus migration tranche due (monthly cadence)? | Sell SGD 20k Maribank PIMCO, deploy 80/20 PIMCO/Amundi |
| 2 | PIMCO trim trigger fired (Hormuz fully open + confirmed ceasefire)? | Execute pre-decided ladder: 30% trim → 40% Gold / 30% CLR / 30% G3B |
| 3 | Gold spot < $4,500? | GLS ladder add SGD 200–500 via LongBridge |
| 4 | Oil < $90 confirmed (2 weeks sustained)? | **Gold add trigger fires** — deploy SGD idle cash into LionGlobal Gold / GLS |
| 5 | CLR yield > 5.5% post-pullback? | Add SGD 500–1,000 via LongBridge |
| 6 | Indo 10Y > 7%? | Bibit SBN top-up next IDR cash batch |
| 7 | VIX > 25? | Freeze all new adds for the week |
| 8 | BTC F&G < 25? (**CoinDesk MCP** for live read) | Small BTC DCA $50–100 |
| 9 | New IDR/SGD income deposit? | Earmark per IPS phase |
| 10 | Wedding fund pre-position window (Sep–Dec 2026)? | Redeem next Makmur tranche, convert IDR→SGD, park in SavePlus |
| 11 | Phase transition trigger met? | Move Phase 1 → 2 (wife arriving) or Phase 2 → 3 (wife employed) |
| 12 | **BUMI exit decision** — mineral export duty finalized? | Execute 2-week exit plan; redeploy to Emas Batang or IDR FI |
| 13 | **LB Cash SGD idle > SGD 3k?** | Move excess to Maribank Saveplus immediately |
| 14 | **IDR MM fund yield < BI rate - 1%?** | Flag for Morningstar review; consider switching to higher-yield MM |

### Block 5 — Logging (5 min)

Append to `weekly-log.md` (in outputs folder or personal Notion/doc):

```
Sat YYYY-MM-DD
Phase: [1 / 2 / 3]
Total book: IDR ____  (SGD ____)
WoW change: ____ (__%)
Wedding fund progress: SGD __ / 20k
Emergency fund: SGD __ / 30k floor
PIMCO % of book: __% (target trajectory: 18% by Sep 2026, 10% by 2027)

Macro flags this week: [list any threshold breaches]
Drift breaches: [list any out-of-band classes]
MCP data used: [CoinDesk ✓/✗ | Morningstar ✓/✗ | FMP ✓/✗]

Actions taken this week:
  - [list]

Actions queued for next Tue-Fri:
  1. ___
  2. ___
  3. ___

Notes: [any unusual observations]
```

---

## Monthly extension (last Saturday of each month)

Add 30 minutes for these tasks:

| Task | How (upgraded) |
|---|---|
| Run **fund reconciliation** for distributing IDR funds | Invoke `yu-portfolio-analyzer` reconcile-only mode. **If Morningstar MCP connected:** pull total-return data directly — skips Bareksa scrape entirely |
| Update **Makmur fund classifications** | Skill `fund_registry.json` update |
| Review **PIMCO migration progress** | vs target pace |
| **Wedding fund cumulative tracker** | Visualize 8-month build |
| **PR application status check** | Affects Phase transition timing |
| Snapshot total book to historical record | Year-on-year comparison |
| Run **risk metrics** (Sharpe/drawdown/HHI) | `yu-portfolio-analyzer` "check risk" mode |
| **FMP fundamentals sweep** (if connected) | Pull trailing P/E, EPS growth, analyst targets for META, NVO, IREN, DCII | Check vs cost basis — are underwater names still fundamentally intact? |
| **Mineral tax monitoring** | Check ESDM announcements for export duty finalization | Affects BUMI exit timing |

---

## Quarterly extension (Mar / Jun / Sep / Dec last Saturday)

Plus:
- **Re-read IPS** end-to-end, check for stale assumptions
- **Review ALL drawdowns > 20%** for hold/cut decisions (standing: COIN -70%, BUMI -50%, CDIA -41%, PANI -37%)
- **Tax / domicile review** — anything that changed?
- **Re-rate Yu's 5-year horizon assumptions** — house, kids, career
- **MSCI review cycle check** — August 2026 next key date

---

## Annual extension (first Saturday of January)

- **Full IPS revision** — formal phase update, target tweaks, life-event sync
- **Performance attribution** — what drove returns this year?
- **Goal review** — wedding done? Child planning? PR achieved?
- **Tax considerations** — SG no CGT; document for Indonesian tax if relevant

---

## How to invoke this skill

User triggers:
- "saturday review"
- "weekly review"
- "weekly check"
- "what's the next action this week"
- "saturday action"
- "weekly routine"
- "run my portfolio review"

Output: structured Markdown checklist with all 5 blocks completed, queued actions for next week, and the log entry ready to copy.

---

## Hard rules during the routine

- ❌ **Don't trade Saturday** — orders fill Mon at unknown prices
- ❌ **Don't read 50 news articles** — top headlines from Block 1 sources only
- ❌ **Don't tinker with IPS targets** — formal revision is annual / life-event
- ❌ **Don't skip the routine on green weeks** — bull-market complacency is the risk
- ❌ **Don't add new lock-up products** (>6 months commitment) until Q3 2027
- ✅ **Do use MCP tools first** (CoinDesk, Morningstar, FMP) before falling back to web search
- ✅ **Do queue actions for Tue-Fri** with specific size + venue
- ✅ **Do log even if nothing happened** — the data accumulates
- ✅ **Do be ruthless about the 30-minute timer** — discipline > thoroughness

---

## Reference: action venue cheat-sheet

| Asset | Venue | Settlement |
|---|---|---|
| PIMCO Maribank → Endowus migration | Sell on Maribank → wire SGD → buy Endowus | T+5 round-trip |
| Endowus Amundi adds | Endowus DIY in-platform | T+1 |
| GLS / CLR / G3B | LongBridge SGX | T+1 |
| LB Cash → Maribank Saveplus | Transfer via banking app | Same day |
| Bibit SBN FR series | Bibit | T+1 |
| Makmur fund redemption | Makmur app | T+2 to T+3 |
| BTC DCA | moomoo | Same-day |
| US stocks (META/NVO/IREN/SOFI/PYPL/SOUN) | moomoo | T+1 |

---

## Reference: triggers checklist (always-checked)

| Trigger | Status (May 2026) | Pre-decided action |
|---|---|---|
| Iran ceasefire / Hormuz fully reopens | 🟡 NEAR — speculation active, Hormuz "open" per Iran | PIMCO trim 30% → 40/30/30 ladder. **Monitor weekly.** |
| Mineral export duty finalized (coal/nickel) | 🟡 PENDING — ESDM coordination ongoing | BUMI exit decision executes once finalized |
| Oil < $90 sustained 2 weeks | 🟡 OIL @ $101, falling from $118 peak | Gold add trigger — watch weekly |
| Gold < $4,500 | Not fired (gold @ $4,715) | GLS ladder tranche |
| Indo 10Y > 7% | Currently ~6.83% | Bibit SBN top-up |
| Warsh confirmed as Fed chair | May 15 2026 formal start | Watch for dovish tone shift → reassess FI duration |
| MSCI freeze lift | Not fired — August 2026 earliest | IDX equity sentiment watch |
| BREN/DSSA MSCI removal | ✅ FIRED — removed May 4 | IDR 15T outflow absorbed; IDX headwind now structural |
| BTC F&G < 25 | Not fired (F&G @ 38–47) | BTC DCA $50–100 |
| SLV trim target | Not fired | Trim half SLV at target price |
| Wife employed in SG | Pending | Phase 2 → 3 transition |
| Yu job change | None | Reset emergency fund target |

---

## MCP upgrade notes (v2 changes)

| What changed | Why |
|---|---|
| CoinDesk MCP replaces manual BTC/F&G check | Live crypto data, no manual lookup |
| Morningstar MCP replaces Bareksa scrape for IDR fund NAV | Morningstar has total-return data natively; Bareksa scraping is fragile |
| FMP MCP replaces Yahoo Finance for earnings calendar + fundamentals | 250 calls/day free; covers all your tickers |
| Mineral tax trigger added to Block 1, 2, 4 | ESDM export duty announcement is active risk for BUMI/NCKL |
| MSCI triggers updated to reflect BREN/DSSA removal (fired May 4) | Stale trigger updated |
| LB Cash → Saveplus trigger added (Decision queue #13) | Idle SGD cash below risk-free rate — standing action |
| Gold add trigger tied to oil level | Cross-check: oil < $90 = gold window open |

End report with: *"Informational analysis, not financial advice."*
