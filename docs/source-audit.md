# Source audit and lean-profile decisions

Status: **Phase 1 done** (lean/full profiles), **Phase 3 done** (contract fixtures),
**Phase 2 pending decisions** (this document). Production defaults to
`DATA_SOURCE_PROFILE=lean`; `full` preserves every declared leg.

## What is external and uncontrollable

| Class | Examples | Notes |
|---|---|---|
| Market data providers | tencent, sina, eastmoney (push2/datacenter/emweb), cninfo, csindex, legulegu, hkex, sse, szse, sec.gov, yfinance | keyless or account/cookie based; rename/rate-limit/HTML-challenge risk |
| Keyed providers | tushare, longbridge, finnhub, alphavantage, lixinger, xueqiu | optional; fail fast when the key is absent |
| Search/sentiment | tavily, brave, bocha, serpapi, searxng, adanos, eastmoney guba | key/self-host; RSS/JSON drift |
| Protocols | HTTP JSON, HTML/JS pages, MCP stdio, CLI stdout JSON, DSH tool schema, OpenAI-compatible API | own protocols are stable; third-party pages are not |
| Runtimes/packages | Python 3.10/3.11, Node 24, akshare/yfinance/pandas, DSH/hosts | drift handled by compat shims + Dependabot |
| Upstream code | Weaxs repository | merged, reviewed, never trusted blindly |

## Candidate items (Phase 2)

| # | Item | Current role | Refs | Lean today | Recommendation | Why / risk |
|---|---|---|---|---|---|---|
| 1 | **baostock** | A-share kline backstop | 18 files | excluded | **remove** | legacy leg, extra dependency, rarely wins; K-line stays tencent + sina + akshare |
| 2 | **baidu hot list** | hot-stocks backstop | 2 files | excluded | **decide** | keeping it restores a second keyless leg; dropping it makes `hot_stocks` fail whenever eastmoney throttles (observed locally) |
| 3 | **TIAA / youzhiyouxing** | US advisory-portfolio metadata and disclosures | 15 files | active (niche) | **remove** | very narrow audience, extra parse paths; removal touches quote path + tests |
| 4 | **adanos sentiment** | HK/US social sentiment | 6 files | active if key | **remove** | unstable third-party, non-core; A-share guba/xueqiu stay |
| 5 | **search engines** | news/sentiment search | 6–9 each | all clients kept | **keep 1–2** | no engine configured today → news search returns empty; recommend one hosted key (Tavily) plus self-hosted SearXNG optional |
| 6 | **northbound flow** | market-level northbound history | 1 tool | active | **keep, mark historical** | exchanges stopped daily publication 2024-08; tool already returns a clean explanation |
| 7 | **JP/KR/TW markets** | yfinance-only quotes/klines | many | active | **keep** | no extra provider cost; user can ignore these markets |
| 8 | **keyed providers** | tushare/longbridge/finnhub/alphavantage/lixinger/xueqiu | many | excluded from lean | **keep as optional** | zero runtime cost without keys; useful when configured (user explicitly wants Xueqiu) |
| 9 | **efinance** | individual fund-flow backstop | few | active | **keep** | it saved fund flow when eastmoney throttled the shared runner IP |
| 10 | **newspaper4k** | article extraction for search results | 4 files | active | **keep** | local library, used by `extract`; no external state |

## Evidence from the lean smoke run

- `hot_stocks` failed under lean (`eastmoney` only) while eastmoney throttled the IP; the full profile would have fallen back to baidu. This is the trade-off behind item 2.
- `fund_flow` survived the same throttle through efinance, which is why item 9 stays.
- HK/US quotes and klines work through keyless Tencent (`00700.HK`, `AAPL`) in lean.

## Xueqiu (keep, needs a token to be useful)

- Social heat (`_xueqiu_heat`) hardcodes `xq_a_token=placeholder`; the endpoint answers 403 without a real token. It should read `XUEQIU_TOKEN` when present and skip otherwise.
- Industry fallback (`_stock_boards_xueqiu`) already requires `XUEQIU_TOKEN`.
- Portfolio metadata (`_quote_tiaa`) needs a real cookie too (400016 without).
- Recommendation: keep Xueqiu as an optional token source, wire the heat leg to `XUEQIU_TOKEN`, and document that the cookie is account-scoped and expires.

## Decisions needed

1. Remove **baostock** (kline backstop)? Recommend yes.
2. Keep **baidu** as the second hot-stocks leg, or accept eastmoney-only? Recommend keep baidu.
3. Remove **TIAA / youzhiyouxing**? Recommend yes.
4. Remove **adanos sentiment**? Recommend yes.
5. Which search engine(s) to keep: **Tavily** (hosted key), **SearXNG** (self-host), both, or none? Recommend Tavily + optional SearXNG.
6. Confirm **Xueqiu stays** and wire `_xueqiu_heat` to `XUEQIU_TOKEN`? Recommend yes.
