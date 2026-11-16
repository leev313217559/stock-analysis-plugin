# Data-source profiles (`lean` / `full`)

Every capability declares its own failover chain next to the capability code. A
**profile** decides which legs actually run, so the default deployment can keep
2–3 keyless, well-maintained providers while `full` preserves the upstream
multi-fallback behavior for debugging and comparisons.

## Selecting a profile

```bash
# default: lean
python tools/stock_data.py quote 600519

# upstream behavior: every declared leg, in declared order
DATA_SOURCE_PROFILE=full python tools/stock_data.py quote 600519
```

The variable is read at call time (no import-time caching), so tests and one-off
commands can switch per process. Unknown values fall back to `lean`.

`DATA_SOURCE_PROFILE` can also live in the dashboard settings (`$DSH_HOME/stock-analysis.env`); every tool
process loads that file at startup.

## Capability matrix (lean)

| capability | kept legs (ordered) |
|---|---|
| `quote_a` | tencent, sina |
| `quote_a_etf` | tencent, akshare_etf, sina |
| `kline_a` | tencent, sina, akshare |
| `snapshot_a` | akshare(eastmoney), sina, tencent |
| `sector_rankings` | eastmoney, ths, sina |
| `sector_constituents` | eastmoney_industry, eastmoney_concept, sina |
| `fund_flow` | eastmoney, efinance |
| `dragon_tiger` | eastmoney, sina |
| `hot_stocks` | eastmoney, baidu |
| `margin_kline` | akshare, efinance |
| `yf_quote_hk` / `yf_kline_hk` | tencent, yfinance |
| `yf_quote_us` / `yf_kline_us` | tencent, yfinance |
| `yf_quote_other` / `yf_kline_other` | yfinance |

`fund_flow` is listed for completeness: individual flow falls back to efinance in
code rather than through `_failover`, and both legs remain enabled.

## Rules

- A chain is filtered by **provider name**, then reordered to the profile's order.
- A profile never empties a chain: if no declared leg matches, the original chain
  is returned unchanged (degrade to "try what exists", never "no source").
- Unknown labels keep their declared chain, so single-source capabilities and
  non-provider chains (for example Sina's indicator variants) are untouched.
- Sticky failover ordering still applies after the profile filter. A sticky
  winner that the profile removed simply stops being preferred.
- Tests default to `DATA_SOURCE_PROFILE=full` (`tests/conftest.py`) because the
  upstream suite encodes keyed legs; `tests/test_source_profiles.py` covers the
  lean selection and ordering explicitly.

## Adding a source

1. Declare it in the capability's chain (in code) as `(name, callable)`.
2. If it should run in lean, add `name` to the capability's list in
   `tools/sources.py` (`LEAN`).
3. If its chain label is new, add it to `LABEL_CAPABILITIES` so `_failover`
   applies the profile.
4. Add a profile test for the ordering/filtering you expect.
