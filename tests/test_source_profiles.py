"""Source-profile selection (lean vs full) and its wiring into failover chains."""

from tools import sources, stock_data


def _legs(*names):
    return [(name, object()) for name in names]


def test_default_profile_filters_and_orders(monkeypatch):
    monkeypatch.delenv("DATA_SOURCE_PROFILE", raising=False)
    chosen = sources.select("quote_a", _legs("akshare", "tushare", "tencent", "sina"))
    assert [name for name, _ in chosen] == ["tencent", "sina"]


def test_full_profile_keeps_declared_chain(monkeypatch):
    monkeypatch.setenv("DATA_SOURCE_PROFILE", "full")
    declared = _legs("akshare", "tushare", "tencent", "sina")
    assert sources.select("quote_a", declared) is declared


def test_unknown_profile_falls_back_to_lean(monkeypatch):
    monkeypatch.setenv("DATA_SOURCE_PROFILE", "turbo")
    chosen = sources.select("kline_a", _legs("akshare", "tushare", "efinance", "tencent", "baostock"))
    assert [name for name, _ in chosen] == ["tencent", "akshare"]


def test_unknown_capability_leaves_chain_untouched(monkeypatch):
    monkeypatch.delenv("DATA_SOURCE_PROFILE", raising=False)
    declared = _legs("only", "legs")
    assert sources.select("no-such-capability", declared) is declared


def test_profile_never_returns_empty_chain(monkeypatch):
    monkeypatch.delenv("DATA_SOURCE_PROFILE", raising=False)
    # A chain with none of the lean legs must survive unchanged, not go empty.
    declared = _legs("legacy-a", "legacy-b")
    assert sources.select("quote_a", declared) is declared


def test_label_mapping_covers_core_chains():
    for label in (
        "quote_a:600519",
        "kline_a:600519",
        "snapshot_a",
        "sector_rankings:industry",
        "sector_constituents:白酒",
        "dragon_tiger:20261116",
        "hot_stocks",
        "margin_turnover:20261116",
    ):
        declared = _legs("x")
        assert sources.select_for_label(label, declared) is declared


def test_failover_uses_lean_chain(monkeypatch):
    monkeypatch.delenv("DATA_SOURCE_PROFILE", raising=False)
    monkeypatch.setattr(stock_data, "_disk_cache_get", lambda key: None)
    monkeypatch.setattr(stock_data, "_disk_cache_set", lambda *a, **k: None)
    called = []

    def leg(name, value):
        def fn():
            called.append(name)
            return value

        return name, fn

    assert stock_data._failover([leg("eastmoney", []), leg("baidu", [{"name": "hot"}])], "hot_stocks") is None
    assert called == ["eastmoney"]


def test_failover_full_profile_keeps_declared_order(monkeypatch):
    monkeypatch.setenv("DATA_SOURCE_PROFILE", "full")
    monkeypatch.setattr(stock_data, "_disk_cache_get", lambda key: None)
    monkeypatch.setattr(stock_data, "_disk_cache_set", lambda *a, **k: None)
    called = []

    def leg(name, value):
        def fn():
            called.append(name)
            return value

        return name, fn

    result = stock_data._failover([leg("eastmoney", []), leg("baidu", [{"name": "hot"}])], "hot_stocks", evidence=False)
    assert called == ["eastmoney", "baidu"]
    assert result == [{"name": "hot"}]


def test_yf_failover_lean_puts_keyless_tencent_first(monkeypatch):
    monkeypatch.delenv("DATA_SOURCE_PROFILE", raising=False)
    called = []

    def leg(name, value):
        def fn():
            called.append(name)
            return value

        return lambda: fn()

    result = stock_data._yf_failover(
        "00700.HK",
        leg("yfinance", {"price": 1}),
        leg("tencent", {"price": 2}),
        leg("finnhub", {"price": 3}),
        leg("longbridge", {"price": 4}),
        leg("alphavantage", {"price": 5}),
        label="quote:00700.HK",
    )
    assert result["price"] == 2
    assert called == ["tencent"]


def test_yf_failover_other_markets_stay_yfinance_only(monkeypatch):
    monkeypatch.delenv("DATA_SOURCE_PROFILE", raising=False)
    called = []

    def leg(name, value):
        def fn():
            called.append(name)
            return value

        return fn

    result = stock_data._yf_failover(
        "7203.T",
        leg("yfinance", {"price": 1}),
        leg("tencent", {"price": 2}),
        leg("finnhub", {"price": 3}),
        leg("longbridge", {"price": 4}),
        leg("alphavantage", {"price": 5}),
        label="quote:7203.T",
    )
    assert result["price"] == 1
    assert called == ["yfinance"]
