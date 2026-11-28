"""Open-end fund NAV helpers (extracted from stock_data.py)."""

import json
import math
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from _subproc import error_message


def _parse_float(value):
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _cn_now() -> datetime:
    return datetime.now(ZoneInfo("Asia/Shanghai"))


def _clean_row(d: dict) -> dict:
    return {k: (None if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v) for k, v in d.items()}


def _fund_js_value(text: str, name: str):
    match = re.search(rf"\b{re.escape(name)}\s*=\s*", text)
    if not match:
        raise ValueError(f"eastmoney fund data missing {name}")
    try:
        return json.JSONDecoder().raw_decode(text[match.end() :])[0]
    except json.JSONDecodeError as exc:
        raise ValueError(f"eastmoney fund data has invalid {name}") from exc


def _fund_nav_date(stamp) -> str:
    return datetime.fromtimestamp(stamp / 1000, timezone.utc).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()


def fund_pingzhong_js(symbol: str) -> str:
    """Eastmoney's per-fund JS bundle (NAV, scale, holdings series)."""
    import requests

    response = requests.get(f"https://fund.eastmoney.com/pingzhongdata/{symbol}.js", timeout=15)
    response.raise_for_status()
    return response.text


def cmd_fund_quote(args, *, trend_count: int = 0, fetch_js=None):
    symbol = args.symbol
    if not re.fullmatch(r"\d{6}", symbol):
        return {"error": "open-end fund symbol must be exactly 6 digits"}
    try:
        text = (fetch_js or fund_pingzhong_js)(symbol)
        if _fund_js_value(text, "fS_code") != symbol:
            raise ValueError(f"eastmoney returned a different fund for {symbol}")
        name = _fund_js_value(text, "fS_name")
        nav_rows = _fund_js_value(text, "Data_netWorthTrend")
        accumulated_rows = [] if trend_count else _fund_js_value(text, "Data_ACWorthTrend")
        points = []
        for row in reversed(nav_rows):
            if not isinstance(row, dict):
                continue
            nav = _parse_float(row.get("y"))
            if nav is None or not math.isfinite(nav) or nav <= 0:
                continue
            try:
                day = _fund_nav_date(row.get("x"))
            except (TypeError, ValueError, OverflowError, OSError):
                continue
            points.append((row, day, nav))
            if len(points) >= max(1, trend_count):
                break
        if not points:
            raise ValueError(f"eastmoney returned no NAV for {symbol}")
        latest, nav_date, nav = points[0]
        accumulated_by_date = {_fund_nav_date(row[0]): row[1] for row in accumulated_rows}
        today = _cn_now().date().isoformat()
        result = _clean_row(
            {
                "symbol": symbol,
                "name": name,
                "asset_type": "open_end_fund",
                "nav": nav,
                "accumulated_nav": accumulated_by_date.get(nav_date),
                "change_pct": latest.get("equityReturn"),
                "nav_date": nav_date,
                "data_as_of": nav_date,
                "as_of": nav_date,
                "as_of_basis": "provider",
                "stale": nav_date < today,
                "source": "eastmoney",
                "source_url": f"https://fund.eastmoney.com/{symbol}.html",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "note": (
                    "nav is published end-of-day NAV, not a real-time price; QDII disclosure may lag "
                    "1-2 trading days; no intraday estimated NAV is provided"
                ),
                # Eastmoney retired its per-fund intraday estimate (fundgz); its remaining estimate
                # page lists every fund at once, so the estimate keys stay but are always unavailable.
                "estimated_nav": None,
                "estimated_change_pct": None,
                "estimated_at": None,
                "estimate_status": "unavailable",
            }
        )
        if trend_count:
            result["trend"] = [{"date": day, "close": nav} for _, day, nav in reversed(points)]
        return result
    except Exception as e:
        return {"error": error_message(e)}
