"""Index chart payload: daily history merged with today's intraday bar."""

from tools import index_chart


def test_today_intraday_is_merged_into_history(monkeypatch):
    monkeypatch.setattr(index_chart, "detect_market", lambda symbol: "A")
    monkeypatch.setattr(
        index_chart,
        "_daily",
        lambda symbol, market, days: [
            {"date": "2026-11-13", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 100, "turnover": 1000},
            {"date": "2026-11-14", "open": 10, "high": 12, "low": 10, "close": 11, "volume": 200, "turnover": 2200},
        ],
    )
    monkeypatch.setattr(
        index_chart,
        "_tencent_minute",
        lambda symbol: {
            "date": "2026-11-16",
            "points": [{"t": "09:30", "price": 11.5}, {"t": "09:31", "price": 12.5}, {"t": "09:32", "price": 12.0}],
            "volume": 300,
            "turnover": 3600,
            "source": "tencent",
            "delayed": False,
        },
    )
    monkeypatch.setattr(index_chart, "_eastmoney_amounts", lambda symbol: {})

    result = index_chart.build("sh000001", 120)

    assert result["market"] == "A"
    assert result["volume_unit"] == "手"
    assert result["turnover_unit"] == "元"
    assert result["history"][-1] == {
        "date": "2026-11-16",
        "open": 11.5,
        "high": 12.5,
        "low": 11.5,
        "close": 12.0,
        "volume": 300,
        "turnover": 3600,
    }
    assert result["prev_close"] == 11
    assert result["intraday"]["prev_close"] == 11
    assert result["intraday"]["points"][-1]["price"] == 12.0


def test_existing_today_bar_is_updated(monkeypatch):
    monkeypatch.setattr(index_chart, "detect_market", lambda symbol: "A")
    monkeypatch.setattr(
        index_chart,
        "_daily",
        lambda symbol, market, days: [
            {"date": "2026-11-13", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 100, "turnover": 1000},
            {"date": "2026-11-16", "open": 11, "high": 12, "low": 10, "close": 11.5, "volume": 250, "turnover": 2800},
        ],
    )
    monkeypatch.setattr(
        index_chart,
        "_tencent_minute",
        lambda symbol: {
            "date": "2026-11-16",
            "points": [{"t": "09:30", "price": 11.2}, {"t": "10:00", "price": 13.0}],
            "volume": 400,
            "turnover": 5000,
            "source": "tencent",
            "delayed": False,
        },
    )
    monkeypatch.setattr(index_chart, "_eastmoney_amounts", lambda symbol: {"2026-11-16": 5100})

    result = index_chart.build("sh000001", 120)

    last = result["history"][-1]
    assert last["date"] == "2026-11-16"
    assert last["close"] == 13.0
    assert last["high"] == 13.0
    assert last["low"] == 10.0
    assert last["turnover"] == 5000
    assert result["prev_close"] == 10
