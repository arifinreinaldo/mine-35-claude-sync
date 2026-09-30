#!/usr/bin/env python3
"""
swing-scanner — data fetcher (runs on YOUR machine, not in Cowork).

Reads a ticker universe, pulls ~14 months of daily OHLCV from Twelve Data,
and writes one flat CSV. You then hand that CSV to the swing-scanner skill,
which does all the scoring/filtering. Your API key never leaves your machine.

Why this lives on your machine: Twelve Data is unreachable from the Cowork
sandbox (allowlist proxy). Your laptop has open network — so the *fetch* runs
here, the *analysis* runs in the skill.

------------------------------------------------------------------------------
SETUP (one time)
------------------------------------------------------------------------------
1. You need Python 3 (any recent version). No pip installs — pure stdlib.
2. Provide your Twelve Data API key one of two ways (env var preferred):
   a) Environment variable (most secure):
        macOS / Linux:   export TWELVEDATA_API_KEY="your_key_here"
        Windows (cmd):   set TWELVEDATA_API_KEY=your_key_here
      (Add the export line to ~/.zshrc or ~/.bashrc to make it permanent.)
   b) A key file next to this script -- default name `env.text` -- one line:
        key=your_key_here
      Keep this file on your machine only. NEVER commit it to git, share it,
      or paste its contents into a chat. Add `env.text` to your .gitignore.
   The env var wins if both are set. The key is never printed or logged.
3. Keep `universe.txt` next to this script (one ticker per line, # = comment).

------------------------------------------------------------------------------
RUN
------------------------------------------------------------------------------
    python3 fetch.py
    # or customise:
    python3 fetch.py --universe universe.txt --out swing_data.csv --days 400

It throttles itself to Twelve Data's free tier (8 requests/min, 800/day).
A ~150-ticker universe takes roughly 18-20 minutes — it prints progress.
When done you'll have `swing_data.csv`. Upload THAT to the swing-scanner skill.

------------------------------------------------------------------------------
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API_BASE = "https://api.twelvedata.com/time_series"
BENCHMARKS = ["SPY", "RSP"]          # always fetched, used by the skill for RS + breadth
FREE_TIER_PER_MIN = 8                # Twelve Data free tier: 8 API credits / minute
FREE_TIER_PER_DAY = 800              # ... and 800 / day


def load_universe(path):
    """One ticker per line; '#' starts a comment; blanks ignored."""
    tickers = []
    with open(path) as f:
        for line in f:
            line = line.split("#", 1)[0].strip().upper()
            if line:
                tickers.append(line)
    # de-dupe, keep order, append benchmarks if missing
    seen, out = set(), []
    for t in tickers + BENCHMARKS:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def fetch_one(symbol, api_key, outputsize):
    """Return list of bar dicts (newest-first from TD) or raise with a clear message."""
    qs = urllib.parse.urlencode({
        "symbol": symbol,
        "interval": "1day",
        "outputsize": outputsize,
        "apikey": api_key,
        "format": "JSON",
    })
    url = f"{API_BASE}?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "swing-scanner/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode())

    # Twelve Data signals problems with status == "error"
    if isinstance(payload, dict) and payload.get("status") == "error":
        code = payload.get("code")
        msg = payload.get("message", "unknown error")
        if code == 429:
            raise RuntimeError(f"RATE_LIMIT: {msg}")
        raise RuntimeError(f"API_ERROR {code}: {msg}")
    values = payload.get("values") if isinstance(payload, dict) else None
    if not values:
        raise RuntimeError("EMPTY: no values returned")
    return values


def load_api_key(env_var, key_file):
    """Resolve the API key: environment variable first, then a key file.

    The key file (default `env.text`) is a simple text file with one line:
        key=your_key_here
    Lines starting with '#' are ignored. The identifier left of '=' may be
    any of: key / apikey / api_key / <env_var> (case-insensitive). The key
    value itself is never printed or logged by this script.
    """
    # 1. environment variable -- most secure, wins if set
    val = os.environ.get(env_var, "").strip()
    if val:
        return val
    # 2. key file fallback
    if key_file and os.path.exists(key_file):
        accepted = {"key", "apikey", "api_key", env_var.lower()}
        try:
            with open(key_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    lhs, rhs = line.split("=", 1)
                    if lhs.strip().lower() in accepted:
                        return rhs.strip().strip('"').strip("'")
        except OSError:
            pass
    return None


def main():
    ap = argparse.ArgumentParser(description="Twelve Data fetcher for swing-scanner")
    ap.add_argument("--universe", default="universe.txt")
    ap.add_argument("--out", default="swing_data.csv")
    ap.add_argument("--days", type=int, default=400,
                    help="calendar days of history (~400 covers a 200-day MA + 1y RS)")
    ap.add_argument("--key-env", default="TWELVEDATA_API_KEY",
                    help="environment variable holding your API key")
    ap.add_argument("--key-file", default="env.text",
                    help="fallback file with a 'key=...' line, used if the env var is unset")
    ap.add_argument("--per-min", type=int, default=FREE_TIER_PER_MIN,
                    help="throttle: requests per minute (free tier = 8)")
    args = ap.parse_args()

    api_key = load_api_key(args.key_env, args.key_file)
    if not api_key:
        sys.exit(f"ERROR: no API key found.\n"
                 f"  Option A:  export {args.key_env}=\"your_key_here\"\n"
                 f"  Option B:  put a line  key=your_key_here  in {args.key_file}\n"
                 f"  (Never hardcode the key in this file or paste it into a chat.)")

    if not os.path.exists(args.universe):
        sys.exit(f"ERROR: universe file not found: {args.universe}")

    tickers = load_universe(args.universe)
    n = len(tickers)
    if n > FREE_TIER_PER_DAY:
        print(f"WARNING: {n} tickers exceeds the ~{FREE_TIER_PER_DAY}/day free-tier "
              f"budget. Trim universe.txt or run over two days.", file=sys.stderr)

    est_min = n / max(args.per_min, 1)
    print(f"Fetching {n} tickers (incl. benchmarks {BENCHMARKS}) — "
          f"~{est_min:.0f} min at {args.per_min}/min throttle.\n")

    rows = []
    failed = []
    interval = 60.0 / max(args.per_min, 1)   # seconds between requests
    for i, sym in enumerate(tickers, 1):
        t0 = time.time()
        try:
            bars = fetch_one(sym, api_key, args.days)
            for b in bars:
                rows.append({
                    "ticker": sym,
                    "date": b.get("datetime"),
                    "open": b.get("open"),
                    "high": b.get("high"),
                    "low": b.get("low"),
                    "close": b.get("close"),
                    "volume": b.get("volume"),
                })
            print(f"  [{i:>3}/{n}] {sym:<8} ok  ({len(bars)} bars)")
        except RuntimeError as e:
            failed.append((sym, str(e)))
            print(f"  [{i:>3}/{n}] {sym:<8} FAIL  {e}", file=sys.stderr)
            if str(e).startswith("RATE_LIMIT"):
                print("  ... rate-limited; sleeping 60s and continuing.", file=sys.stderr)
                time.sleep(60)
        except Exception as e:                # network / parse / timeout
            failed.append((sym, repr(e)))
            print(f"  [{i:>3}/{n}] {sym:<8} FAIL  {e!r}", file=sys.stderr)

        # throttle: keep average pace under the per-minute cap
        if i < n:
            elapsed = time.time() - t0
            if elapsed < interval:
                time.sleep(interval - elapsed)

    # write the single flat CSV the skill expects
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ticker", "date", "open", "high", "low", "close", "volume"])
        w.writeheader()
        w.writerows(rows)

    ok = n - len(failed)
    print(f"\nDone. {ok}/{n} tickers fetched, {len(rows)} rows -> {args.out}")
    if failed:
        print(f"{len(failed)} failed (excluded from the CSV):")
        for sym, why in failed:
            print(f"   {sym}: {why}")
    print(f"\nNext: upload {args.out} to the swing-scanner skill in Cowork.")


if __name__ == "__main__":
    main()
