#!/usr/bin/env python3
"""
swing-scanner compute engine.

Reads ONE flat CSV produced by fetch.py (columns: ticker,date,open,high,low,
close,volume — many tickers stacked), computes trend / relative-strength /
volatility metrics + a composite Swing Score, detects three public
buyer-appropriate setups, computes universe-level breadth, and writes
results.json.

Pure stdlib — no pandas — so it runs anywhere. The skill (Claude, in Cowork)
runs this on the CSV the user uploads. This script does ONLY the deterministic
math, so none of it has to be re-derived by reasoning.

Usage:
    python3 scan.py --csv swing_data.csv --out results.json [--benchmark SPY]
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from statistics import mean

# ----- tunables (kept here, documented, so the model is transparent) ---------
TRADING_DAYS = {"1m": 21, "3m": 63, "6m": 126, "1y": 252}
STAGE_MA = 150          # ~30-week MA, Weinstein stage analysis
STAGE_SLOPE_LOOKBACK = 20
STAGE_SLOPE_UP = 0.02   # +2% over the lookback => rising
STAGE_SLOPE_DOWN = -0.02
NEAR_HIGH = -0.15       # within 15% of 52w high = "constructive zone"
EXTENDED_ABOVE_50 = 1.20
PARABOLIC_3M = 0.60
NO_BASE_3M = 0.40
NO_BASE_MAX_DD = 0.08   # <8% drawdown over 3m + big run => no base, straight up
MIN_BARS = 60           # below this, ticker is flagged low-sample

# composite Swing Score weights (sum = 1.0)
W_RS = 0.35
W_STAGE = 0.25
W_ALIGN = 0.15
W_VOLSIG = 0.15
W_VCP = 0.10


def sma(values, n):
    if len(values) < n:
        return None
    return mean(values[-n:])


def load_all_from_csv(path):
    """
    Read fetch.py's flat CSV. Returns {ticker: {dates,open,high,low,close,volume}}
    with each list sorted ascending by date. Rows with bad/missing numbers are
    dropped defensively.
    """
    buckets = defaultdict(list)
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            need = {"ticker", "date", "open", "high", "low", "close", "volume"}
            if not need.issubset(set(reader.fieldnames or [])):
                sys.exit(f"ERROR: CSV missing required columns. Need {sorted(need)}, "
                         f"got {reader.fieldnames}")
            for row in reader:
                try:
                    bar = {
                        "date": row["date"],
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": float(row["volume"]),
                    }
                except (TypeError, ValueError):
                    continue  # skip malformed bar
                buckets[row["ticker"].strip().upper()].append(bar)
    except FileNotFoundError:
        sys.exit(f"ERROR: CSV not found: {path}")

    series = {}
    for tkr, bars in buckets.items():
        if not bars:
            continue
        bars.sort(key=lambda b: b["date"])  # ascending
        series[tkr] = {
            "dates": [b["date"] for b in bars],
            "open": [b["open"] for b in bars],
            "high": [b["high"] for b in bars],
            "low": [b["low"] for b in bars],
            "close": [b["close"] for b in bars],
            "volume": [b["volume"] for b in bars],
        }
    return series


def pct(a, b):
    """a/b - 1, safe."""
    if b in (0, None) or a is None:
        return None
    return a / b - 1.0


def classify_stage(closes):
    """Weinstein-style stage from price vs 150-day MA and that MA's slope."""
    ma = sma(closes, STAGE_MA)
    if ma is None:
        return None, None
    ma_then = sma(closes[:-STAGE_SLOPE_LOOKBACK], STAGE_MA) if len(closes) > STAGE_MA + STAGE_SLOPE_LOOKBACK else None
    slope = pct(ma, ma_then) if ma_then else 0.0
    price = closes[-1]
    above = price > ma
    if above and slope > STAGE_SLOPE_UP:
        return 2, slope        # advancing — the only buyable stage
    if (not above) and slope < STAGE_SLOPE_DOWN:
        return 4, slope        # declining
    if above and slope <= STAGE_SLOPE_UP:
        return 3, slope        # topping / rolling over
    return 1, slope            # basing / flat


def volatility_contraction(highs, lows, volumes):
    """VCP-ish score 0-3: are the last three ~10-bar ranges progressively
    tighter? Non-declining volume caps the score at 2."""
    if len(highs) < 35:
        return 0
    windows = []
    for i in (30, 20, 10):
        seg_h = highs[-i:-i + 10] if i > 10 else highs[-10:]
        seg_l = lows[-i:-i + 10] if i > 10 else lows[-10:]
        if not seg_h or not seg_l:
            return 0
        rng = (max(seg_h) - min(seg_l)) / max(min(seg_l), 1e-9)
        windows.append(rng)
    score = 0
    if windows[1] < windows[0]:
        score += 1
    if windows[2] < windows[1]:
        score += 1
    if windows[2] == min(windows):
        score += 1
    vol_recent = mean(volumes[-10:])
    vol_prior = mean(volumes[-30:-10])
    if vol_recent >= vol_prior:
        score = min(score, 2)
    return score


def volume_signature(closes, volumes, n=50):
    """Up-day volume vs down-day volume over trailing n bars. >1 = accumulation."""
    if len(closes) < n + 1:
        n = len(closes) - 1
    if n < 5:
        return None
    up = down = 0.0
    for i in range(len(closes) - n, len(closes)):
        if closes[i] > closes[i - 1]:
            up += volumes[i]
        elif closes[i] < closes[i - 1]:
            down += volumes[i]
    if down == 0:
        return 2.0
    return up / down


def max_drawdown(closes):
    peak = closes[0]
    mdd = 0.0
    for c in closes:
        peak = max(peak, c)
        mdd = min(mdd, c / peak - 1.0)
    return mdd  # negative


def compute_ticker(sym, s, bench_closes_by_date):
    closes, highs, lows, vols, dates = s["close"], s["high"], s["low"], s["volume"], s["dates"]
    n = len(closes)
    m = {"ticker": sym, "bars": n, "last_date": dates[-1], "price": closes[-1],
         "low_sample": n < MIN_BARS}

    m["sma10"] = sma(closes, 10)
    m["sma20"] = sma(closes, 20)
    m["sma50"] = sma(closes, 50)
    m["sma200"] = sma(closes, 200)

    stage, slope = classify_stage(closes)
    m["stage"] = stage
    m["stage_ma_slope"] = round(slope, 4) if slope is not None else None

    a = m["sma10"], m["sma20"], m["sma50"], m["sma200"]
    m["ma_aligned"] = all(x is not None for x in a) and a[0] > a[1] > a[2] > a[3] and closes[-1] > a[0]

    m["ret_1m"] = pct(closes[-1], closes[-1 - TRADING_DAYS["1m"]]) if n > TRADING_DAYS["1m"] else None
    m["ret_3m"] = pct(closes[-1], closes[-1 - TRADING_DAYS["3m"]]) if n > TRADING_DAYS["3m"] else None
    m["ret_6m"] = pct(closes[-1], closes[-1 - TRADING_DAYS["6m"]]) if n > TRADING_DAYS["6m"] else None

    hi_window = highs[-TRADING_DAYS["1y"]:] if n >= TRADING_DAYS["1y"] else highs
    m["high_52w"] = max(hi_window)
    m["dist_from_high"] = pct(closes[-1], m["high_52w"])

    m["vcp_score"] = volatility_contraction(highs, lows, vols)
    m["vol_signature"] = volume_signature(closes, vols)

    rs_line = []
    for i, d in enumerate(dates):
        b = bench_closes_by_date.get(d)
        if b:
            rs_line.append(closes[i] / b)
    m["rs_line_last"] = rs_line[-1] if rs_line else None
    m["rs_new_high"] = bool(rs_line) and len(rs_line) >= 63 and rs_line[-1] >= max(rs_line[-63:])

    flags = []
    if m["ret_3m"] is not None and m["ret_3m"] > PARABOLIC_3M:
        flags.append("PARABOLIC")
    if (m["ret_3m"] is not None and m["ret_3m"] > NO_BASE_3M
            and n > TRADING_DAYS["3m"] and max_drawdown(closes[-TRADING_DAYS["3m"]:]) > -NO_BASE_MAX_DD):
        flags.append("NO_BASE")
    if m["sma50"] and closes[-1] > m["sma50"] * EXTENDED_ABOVE_50:
        flags.append("EXTENDED")
    if stage == 4:
        flags.append("STAGE_4")
    m["risk_flags"] = flags
    return m


def detect_setups(m, s):
    """Attach setups, each with an entry trigger and a stop. No stop => not a setup."""
    closes, highs, lows = s["close"], s["high"], s["low"]
    setups = []
    price = closes[-1]

    if (m["stage"] == 2 and m["dist_from_high"] is not None
            and m["dist_from_high"] > NEAR_HIGH and m["vcp_score"] >= 2):
        win_h, win_l = max(highs[-15:]), min(lows[-15:])
        setups.append({"name": "tight_near_highs",
                       "entry_trigger": round(win_h * 1.001, 2),
                       "stop": round(win_l * 0.99, 2)})

    if (m["stage"] == 2 and m["sma50"] and abs(pct(price, m["sma50"])) < 0.03):
        ma50_then = sma(closes[:-STAGE_SLOPE_LOOKBACK], 50)
        if ma50_then is not None and m["sma50"] > ma50_then:
            setups.append({"name": "pullback_to_50dma",
                           "entry_trigger": round(m["sma50"] * 1.01, 2),
                           "stop": round(m["sma50"] * 0.97, 2)})

    if m["stage"] in (1, 2) and len(closes) >= 45:
        base = closes[-45:-1]
        base_h, base_l = max(base), min(base)
        if (base_h - base_l) / base_h < 0.25 and price >= base_h * 0.97 and m.get("rs_new_high"):
            setups.append({"name": "base_breakout",
                           "entry_trigger": round(base_h * 1.002, 2),
                           "stop": round(base_l * 0.99, 2)})
    return setups


def stage_score(stage):
    return {2: 100, 1: 60, 3: 30, 4: 0}.get(stage, 40)


def volsig_score(vs):
    if vs is None:
        return 50
    return max(0, min(100, (vs - 0.5) / 1.5 * 100))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="swing_data.csv from fetch.py")
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--benchmark", default="SPY")
    args = ap.parse_args()

    series = load_all_from_csv(args.csv)
    if not series:
        sys.exit("ERROR: no usable rows in the CSV.")

    bench = series.get(args.benchmark.upper())
    if bench is None:
        print(f"WARNING: benchmark {args.benchmark} not in CSV — relative strength disabled",
              file=sys.stderr)
        bench_by_date = {}
    else:
        bench_by_date = dict(zip(bench["dates"], bench["close"]))

    skip = {args.benchmark.upper(), "RSP"}
    metrics = {}
    for sym, s in series.items():
        if sym in skip:
            continue
        m = compute_ticker(sym, s, bench_by_date)
        m["setups"] = detect_setups(m, s)
        metrics[sym] = m

    if not metrics:
        sys.exit("ERROR: CSV had only benchmark rows — nothing to rank.")

    # relative-strength percentile across the universe
    rs_vals = sorted(m["rs_line_last"] for m in metrics.values() if m["rs_line_last"] is not None)
    for m in metrics.values():
        if m["rs_line_last"] is None or not rs_vals:
            m["rs_pctile"] = None
        else:
            below = sum(1 for v in rs_vals if v < m["rs_line_last"])
            m["rs_pctile"] = round(below / len(rs_vals) * 99)

    # composite Swing Score
    for m in metrics.values():
        rs = m["rs_pctile"] if m["rs_pctile"] is not None else 50
        sc = (W_RS * rs
              + W_STAGE * stage_score(m["stage"])
              + W_ALIGN * (100 if m["ma_aligned"] else 35)
              + W_VOLSIG * volsig_score(m["vol_signature"])
              + W_VCP * (m["vcp_score"] / 3 * 100))
        m["swing_score"] = round(sc, 1)

    # universe breadth
    priced = list(metrics.values())
    n = len(priced) or 1
    above_50 = sum(1 for m in priced if m["sma50"] and m["price"] > m["sma50"])
    above_200 = sum(1 for m in priced if m["sma200"] and m["price"] > m["sma200"])
    spy_50 = rsp_50 = None
    if bench and len(bench["close"]) > 50:
        spy_50 = pct(bench["close"][-1], bench["close"][-51])
    rsp = series.get("RSP")
    if rsp and len(rsp["close"]) > 50:
        rsp_50 = pct(rsp["close"][-1], rsp["close"][-51])

    breadth = {
        "universe_priced": n,
        "pct_above_50dma": round(above_50 / n * 100, 1),
        "pct_above_200dma": round(above_200 / n * 100, 1),
        "spy_50d_return": round(spy_50, 4) if spy_50 is not None else None,
        "rsp_50d_return": round(rsp_50, 4) if rsp_50 is not None else None,
        "leadership": ("narrow" if (spy_50 is not None and rsp_50 is not None and spy_50 > rsp_50)
                       else "broad" if spy_50 is not None and rsp_50 is not None else "unknown"),
        "weak_breadth_warning": (above_50 / n) < 0.40,
    }

    ranked = sorted(metrics.values(), key=lambda m: m["swing_score"], reverse=True)
    out = {
        "as_of": max((m["last_date"] for m in priced), default=None),
        "breadth": breadth,
        "tickers": ranked,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {args.out}: {n} ranked, breadth {breadth['pct_above_50dma']}% > 50dma, "
          f"as_of {out['as_of']}")


if __name__ == "__main__":
    main()
