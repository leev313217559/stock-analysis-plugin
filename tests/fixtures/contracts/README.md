# Normalized output fixtures

Snapshots of real CLI output, used by `tests/test_output_contracts.py` to assert
shape and types offline. Values and dates are a point-in-time record only and are
never asserted.

Refresh (from the repo root, with the tool venv):

```bash
F=tests/fixtures/contracts
python tools/stock_data.py quote 600519 > $F/quote_cn.json
python tools/stock_data.py kline 600519 --count 5 > $F/kline_cn.json
python tools/stock_data.py market_indices --region cn > $F/indices_cn.json
python tools/stock_data.py market_stats > $F/market_stats.json
python tools/stock_data.py capital_flow 600519 > $F/fund_flow_cn.json
python tools/stock_data.py limit_up_pool > $F/limit_up_pool.json
python tools/trading_calendar.py check CN > $F/calendar_cn.json
python tools/value_data.py index_valuation 000300 --years 1 > $F/index_valuation.json
python tools/stock_data.py sector_rankings --board-type industry --top 5 > $F/sector_rankings.json
python tools/stock_data.py quote 00700.HK > $F/quote_hk.json
python tools/stock_data.py quote AAPL > $F/quote_us.json
```

Refreshing is only needed when the normalized contract intentionally changes.
