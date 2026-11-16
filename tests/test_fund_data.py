from argparse import Namespace
from types import SimpleNamespace

import pandas as pd
import requests

from tools import stock_data


def test_fund_quote_returns_published_nav_with_provider_date(monkeypatch):
    body = """
        var fS_name = "建信新兴市场混合(QDII)C";
        var fS_code = "018147";
        var Data_netWorthTrend = [
            {"x":1703952000000,"y":1.998,"equityReturn":-2.77,"unitMoney":""},
            {"x":1704038400000,"y":2.010,"equityReturn":0.60,"unitMoney":""}
        ];
        var Data_ACWorthTrend = [[1703952000000,1.998],[1704038400000,2.010]];
    """
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: SimpleNamespace(text=body, raise_for_status=lambda: None),
    )
    monkeypatch.setattr(
        "akshare.fund_value_estimation_em",
        lambda: pd.DataFrame(),
    )

    result = stock_data.cmd_fund_quote(Namespace(symbol="018147"))

    assert result["symbol"] == "018147"
    assert result["name"] == "建信新兴市场混合(QDII)C"
    assert result["asset_type"] == "open_end_fund"
    assert result["nav"] == 2.01
    assert result["accumulated_nav"] == 2.01
    assert result["change_pct"] == 0.6
    assert result["nav_date"] == "2024-01-01"
    assert result["data_as_of"] == "2024-01-01"
    assert result["as_of"] == "2024-01-01"
    assert result["as_of_basis"] == "provider"
    assert result["stale"] is True
    assert result["source"] == "eastmoney"
    assert result["source_url"] == "https://fund.eastmoney.com/018147.html"
    assert result["fetched_at"].endswith("+00:00")
    assert result["estimated_nav"] is None
    assert result["estimated_at"] is None
    assert result["estimate_status"] == "unavailable"
    assert "not a real-time price" in result["note"]
    assert "QDII" in result["note"]
    assert "price" not in result


def test_fund_quote_keeps_intraday_estimate_separate_from_official_nav(monkeypatch):
    body = """
        var fS_name = "示例指数基金";
        var fS_code = "018147";
        var Data_netWorthTrend = [{"x":1704038400000,"y":2.010,"equityReturn":0.60,"unitMoney":""}];
        var Data_ACWorthTrend = [[1704038400000,2.010]];
    """
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: SimpleNamespace(text=body, raise_for_status=lambda: None),
    )
    monkeypatch.setattr(
        "akshare.fund_value_estimation_em",
        lambda: pd.DataFrame(
            {
                "基金代码": ["018147"],
                "2024-01-02-估算数据-估算值": ["2.02"],
                "2024-01-02-估算数据-估算增长率": ["0.50%"],
            }
        ),
    )

    result = stock_data.cmd_fund_quote(Namespace(symbol="018147"))

    assert result["nav"] == 2.01
    assert result["nav_date"] == "2024-01-01"
    assert result["data_as_of"] == "2024-01-01"
    assert result["estimated_nav"] == 2.02
    assert result["estimated_change_pct"] == 0.5
    assert result["estimated_at"] == "2024-01-02"
    assert result["estimate_status"] == "available"
    assert "price" not in result


def test_fund_quote_placeholder_estimate_is_unavailable(monkeypatch):
    body = """
        var fS_name = "示例指数基金";
        var fS_code = "018147";
        var Data_netWorthTrend = [{"x":1704038400000,"y":2.010,"equityReturn":0.60,"unitMoney":""}];
        var Data_ACWorthTrend = [[1704038400000,2.010]];
    """
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: SimpleNamespace(text=body, raise_for_status=lambda: None),
    )
    monkeypatch.setattr(
        "akshare.fund_value_estimation_em",
        lambda: pd.DataFrame(
            {
                "基金代码": ["018147"],
                "2024-01-02-估算数据-估算值": ["---"],
                "2024-01-02-估算数据-估算增长率": ["---"],
            }
        ),
    )

    result = stock_data.cmd_fund_quote(Namespace(symbol="018147"))

    assert result["nav"] == 2.01
    assert result["estimated_nav"] is None
    assert result["estimated_change_pct"] is None
    assert result["estimated_at"] is None
    assert result["estimate_status"] == "unavailable"


def test_quote_failure_for_six_digit_code_points_to_fund_quote(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise ValueError("sina: no quote; tencent: no quote")

    monkeypatch.setattr(stock_data, "quote_a", unavailable)
    result = stock_data.cmd_quote(Namespace(symbol="018147"))
    assert result["error"].startswith("sina: no quote"), "provider evidence stays in the error key"
    assert "get_fund_quote" in result["hint"] and "018147" in result["hint"]

    assert "hint" not in stock_data.cmd_quote(Namespace(symbol="600519")), "stock-only prefixes keep the bare error"

    monkeypatch.setattr(stock_data, "quote_yf", unavailable)
    us = stock_data.cmd_quote(Namespace(symbol="AAPL"))
    assert "hint" not in us, "only six-digit codes can be open-end funds"
