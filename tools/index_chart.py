#!/usr/bin/env python3
"""Index chart payload: 120 daily bars + today's intraday points.

A/HK intraday comes from Tencent's minute endpoint (near real-time); US/JP/KR/TW
use yfinance 1-minute history (usually delayed). Daily bars come from the
existing stock_data kline providers; today's incomplete bar is merged from the
intraday series so the 120-day chart includes the current session.
"""

import argparse
import contextlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _subproc import utf8_stdio  # noqa: E402
from stock_data import detect_market, kline_a, kline_yf  # noqa: E402

MARKET_META = {
    "A": {"currency": "CNY", "volume_unit": "手", "turnover_unit": "元"},
    "HK": {"currency": "HKD", "volume_unit": "股", "turnover_unit": "港元"},
    "US": {"currency": "USD", "volume_unit": "股", "turnover_unit": "美元"},
    "JP": {"currency": "JPY", "volume_unit": "股", "turnover_unit": "日元"},
    "KR": {"currency": "KRW", "volume_unit": "股", "turnover_unit": "韩元"},
    "TW": {"currency": "TWD", "volume_unit": "股", "turnover_unit": "新台币"},
}
TENCENT_HK = {"^HSI": "hkHSI", "^HSTECH": "hkHSTECH", "^HSCE": "hkHSCE"}
EASTMONEY_A = {"sh000001": "1.000001", "sz399001": "0.399001", "sz399006": "0.399006"}
INDEX_MARKETS = {
    "^HSI": "HK",
    "^HSCE": "HK",
    "^HSTECH": "HK",
    "^DJI": "US",
    "^IXIC": "US",
    "^GSPC": "US",
    "^RUT": "US",
    "^N225": "JP",
    "^TOPX": "JP",
    "^KS11": "KR",
    "^KQ11": "KR",
    "^TWII": "TW",
}
MARKET_TZ = {
    "A": "Asia/Shanghai",
    "HK": "Asia/Hong_Kong",
    "US": "America/New_York",
    "JP": "Asia/Tokyo",
    "KR": "Asia/Seoul",
    "TW": "Asia/Taipei",
}


def _date_from_stamp(value) -> str:
    text = str(value or "").strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:]}"
    return text[:10]


def _tencent_minute(symbol: str) -> dict:
    import requests

    market = detect_market(symbol)
    code = symbol.lower() if market == "A" else TENCENT_HK.get(symbol.upper())
    if not code:
        raise ValueError(f"no Tencent minute mapping for {symbol}")
    response = requests.get(
        "https://web.ifzq.gtimg.cn/appstock/app/minute/query",
        params={"code": code},
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    node = (response.json().get("data") or {}).get(code) or {}
    payload = node.get("data") or {}
    raw = payload.get("data") or []
    points = []
    last_volume = None
    last_turnover = None
    for row in raw:
        parts = str(row).split()
        if len(parts) < 2:
            continue
        try:
            price = float(parts[1])
        except ValueError:
            continue
        if price <= 0:
            continue
        hhmm = parts[0].zfill(4)
        points.append({"t": f"{hhmm[:2]}:{hhmm[2:]}", "price": price})
        if len(parts) >= 3:
            with contextlib.suppress(ValueError):
                last_volume = float(parts[2])
        if len(parts) >= 4:
            with contextlib.suppress(ValueError):
                last_turnover = float(parts[3])
    if not points:
        raise ValueError("Tencent minute data is empty")
    date = _date_from_stamp(payload.get("date") or node.get("date"))
    if not date:
        date = datetime.now(ZoneInfo(MARKET_TZ.get(market, "Asia/Shanghai"))).date().isoformat()
    return {
        "date": date,
        "points": points,
        "volume": last_volume,
        "turnover": last_turnover,
        "source": "tencent",
        "delayed": False,
        "delay_minutes": 0,
    }


def _yf_minute(symbol: str) -> dict:
    import yfinance as yf

    frame = yf.Ticker(symbol).history(period="1d", interval="1m", prepost=False)
    if frame is None or frame.empty:
        raise ValueError("yfinance minute data is empty")
    points = []
    volumes = []
    for index, row in frame.iterrows():
        close = row.get("Close")
        if close is None or float(close) <= 0:
            continue
        points.append({"t": index.strftime("%H:%M"), "price": float(close)})
        volume = row.get("Volume")
        if volume is not None:
            volumes.append(float(volume))
    if not points:
        raise ValueError("yfinance minute data has no prices")
    return {
        "date": frame.index[-1].strftime("%Y-%m-%d"),
        "points": points,
        "volume": sum(volumes) if volumes else None,
        "turnover": None,
        "source": "yfinance",
        "delayed": True,
        "delay_minutes": 15,
    }


def _eastmoney_amounts(symbol: str) -> dict:
    """A-share index daily amount history; silently empty when the source fails."""
    secid = EASTMONEY_A.get(symbol.lower())
    if not secid:
        return {}
    import requests

    try:
        response = requests.get(
            "https://push2his.eastmoney.com/api/qt/stock/kline/get",
            params={
                "secid": secid,
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
                "klt": "101",
                "fqt": "1",
                "end": "20500101",
                "lmt": "180",
            },
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"},
        )
        response.raise_for_status()
        rows = (response.json().get("data") or {}).get("klines") or []
        result = {}
        for row in rows:
            parts = str(row).split(",")
            if len(parts) >= 7:
                result[parts[0]] = float(parts[6])
        return result
    except Exception:
        return {}


def _daily(symbol: str, market: str, days: int) -> list:
    if market == "A":
        rows = kline_a(symbol, "daily", days, evidence=True)
    else:
        rows = kline_yf(symbol, "daily", days, evidence=True)
    return [row for row in (rows or []) if row.get("date")]


def build(symbol: str, days: int = 120) -> dict:
    market = INDEX_MARKETS.get(symbol.upper(), detect_market(symbol))
    meta = MARKET_META.get(market, MARKET_META["A"])
    history = _daily(symbol, market, days)
    if not history:
        raise ValueError(f"no daily history for {symbol}")

    if market in ("A", "HK"):
        try:
            intraday = _tencent_minute(symbol)
        except Exception:
            intraday = _yf_minute(symbol)
    else:
        intraday = _yf_minute(symbol)

    amounts = _eastmoney_amounts(symbol) if market == "A" else {}
    if amounts:
        for bar in history:
            if bar.get("turnover") is None:
                bar["turnover"] = amounts.get(str(bar.get("date")))

    today = intraday["date"]
    last = history[-1]
    prices = [point["price"] for point in intraday["points"]]
    if today and last.get("date") == today:
        last["close"] = prices[-1]
        last["high"] = max(float(last.get("high") or prices[-1]), max(prices))
        last["low"] = min(float(last.get("low") or prices[-1]), min(prices))
        if intraday.get("turnover") is not None:
            last["turnover"] = intraday["turnover"]
    elif today and str(last.get("date")) < today:
        history.append(
            {
                "date": today,
                "open": prices[0],
                "high": max(prices),
                "low": min(prices),
                "close": prices[-1],
                "volume": intraday.get("volume"),
                "turnover": intraday.get("turnover"),
            }
        )

    history = history[-days:]
    today_bar = history[-1] if history and history[-1].get("date") == today else None
    prev = history[-2]["close"] if today_bar and len(history) >= 2 else (history[-1]["close"] if history else None)
    for bar in history:
        if bar.get("turnover") is not None:
            bar["turnover"] = round(float(bar["turnover"]), 2)
    return {
        "symbol": symbol,
        "market": market,
        "currency": meta["currency"],
        "volume_unit": meta["volume_unit"],
        "turnover_unit": meta["turnover_unit"],
        "source": history[-1].get("source") or intraday["source"],
        "delayed": bool(intraday.get("delayed")),
        "delay_minutes": intraday.get("delay_minutes", 0),
        "as_of": f"{today} {intraday['points'][-1]['t']}" if today else None,
        "prev_close": prev,
        "intraday": {**intraday, "prev_close": prev},
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser(description="Index 120-day + intraday chart payload")
    parser.add_argument("symbol")
    parser.add_argument("--days", type=int, default=120)
    args = parser.parse_args()
    try:
        result = build(args.symbol, max(20, min(args.days, 250)))
    except Exception as exc:
        result = {"error": str(exc)}
    json.dump(result, sys.stdout, ensure_ascii=False, default=str)
    print()
    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    utf8_stdio()
    main()
