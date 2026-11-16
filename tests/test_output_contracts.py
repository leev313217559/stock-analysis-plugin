"""Normalized output contracts for the core CLI tools.

Fixtures are snapshots captured from a real run; tests assert **shape and type**,
never values or freshness. A provider column rename or a normalizer regression
fails here offline, while live drift is covered by the scheduled canary.
"""

import json
from datetime import date, datetime
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "contracts"


def load(name: str):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def is_num(value) -> bool:
    return isinstance(value, (int, float)) and value == value


def parse_day(value: str) -> date:
    return datetime.fromisoformat(str(value)[:10]).date()


def test_quote_contract():
    for name in ("quote_cn", "quote_hk", "quote_us"):
        data = load(name)
        assert isinstance(data, dict), name
        assert isinstance(data.get("name"), str) and data["name"], name
        assert is_num(data.get("price")) and data["price"] > 0, name
        assert is_num(data.get("change_pct")), name
        assert isinstance(data.get("source"), str) and data["source"], name
        assert parse_day(data["data_as_of"]), name


def test_kline_contract():
    rows = load("kline_cn")
    assert isinstance(rows, list) and rows, "kline must be a non-empty list"
    row = rows[0]
    for field in ("date", "open", "high", "low", "close", "volume"):
        assert field in row, f"missing {field}"
    assert is_num(row["close"]) and row["close"] > 0
    assert parse_day(row["date"])


def test_indices_contract():
    rows = load("indices_cn")
    assert isinstance(rows, list) and len(rows) >= 5
    for row in rows:
        assert isinstance(row.get("code"), str) and row["code"]
        assert isinstance(row.get("name"), str) and row["name"]
        assert is_num(row.get("price")) and row["price"] > 0


def test_market_stats_contract():
    data = load("market_stats")
    total = data["total_stocks"]
    assert is_num(total) and total > 1000
    up, down, flat = data["up_count"], data["down_count"], data["flat_count"]
    assert all(is_num(v) for v in (up, down, flat))
    assert abs((up + down + flat) - total) <= max(10, total * 0.02)
    assert is_num(data["total_turnover"]) and data["total_turnover"] > 0
    assert is_num(data["limit_up_count"]) and is_num(data["limit_down_count"])


def test_fund_flow_contract():
    rows = load("fund_flow_cn")
    assert isinstance(rows, list) and rows
    assert is_num(rows[0].get("main_net_inflow"))


def test_limit_up_pool_contract():
    data = load("limit_up_pool")
    assert isinstance(data, dict)
    assert isinstance(data.get("date"), str) and len(data["date"]) == 8
    assert is_num(data.get("count")) and data["count"] >= 0
    assert isinstance(data.get("pool"), list)


def test_calendar_contract():
    data = load("calendar_cn")
    assert isinstance(data.get("is_trading_day"), bool)


def test_index_valuation_contract():
    data = load("index_valuation")
    assert isinstance(data, dict)
    assert isinstance(data.get("history"), list) or isinstance(data.get("metrics"), dict)
    assert data.get("source")


def test_sector_rankings_contract():
    rows = load("sector_rankings")
    assert isinstance(rows, list) and rows
    assert isinstance(rows[0].get("name"), str) and rows[0]["name"]
    assert is_num(rows[0].get("change_pct"))
