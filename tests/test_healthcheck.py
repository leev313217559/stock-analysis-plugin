"""Canary validators keep real data gaps as warnings, not hard failures."""

from scripts.healthcheck import check_market_stats


def _stats(**overrides):
    base = {
        "total_stocks": 5930,
        "up_count": 1326,
        "down_count": 4119,
        "flat_count": 131,
        "total_turnover": 1_500_000_000_000,
    }
    base.update(overrides)
    return base


def test_market_stats_allows_suspended_rows_without_change_pct():
    status, detail = check_market_stats(_stats())
    assert status == "warn"
    assert "unpriced rows" in detail["warnings"][0]


def test_market_stats_exact_breadth_is_ok():
    status, detail = check_market_stats(_stats(total_stocks=5576))
    assert status == "ok"
    assert detail["total"] == 5576


def test_market_stats_breadth_exceeding_total_is_fail():
    status, detail = check_market_stats(_stats(up_count=6000))
    assert status == "fail"
    assert any("exceeds total" in problem for problem in detail["problems"])
