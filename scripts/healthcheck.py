#!/usr/bin/env python3
"""Production healthcheck for the market-data layer.

Runs a fixed set of real CLI calls (the same paths the DSH/OpenClaw/Pi tools
use), validates the JSON shape and freshness, and exits non-zero when a hard
check fails. Rate limits and empty off-hours pools are reported as warnings so
a transient throttle does not page anyone.

Usage:
    python scripts/healthcheck.py                 # human summary + JSON file optional
    python scripts/healthcheck.py --json          # JSON to stdout (for CI)
    python scripts/healthcheck.py --out hc.json   # also write JSON to a path
    python scripts/healthcheck.py --strict        # warnings also fail the run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

# Transient upstream conditions: rate limits, proxy/CDN challenge pages, and
# gateways that answer with HTML instead of JSON. These warn instead of failing
# so a shared runner IP being throttled does not page anyone.
TRANSIENT_MARKERS = (
    "限流",
    "RateLimit",
    "Push2RateLimit",
    "断开了连接",
    "RemoteDisconnected",
    "timed out",
    "Timeout",
    "rate limit",
    "Expecting value",
    "Expecting property name",
    "JSONDecodeError",
    "Unexpected token",
    "502 Bad Gateway",
    "503 Service",
    "504 Gateway",
    "Connection reset",
    "ProxyError",
)


def _num(value) -> bool:
    return isinstance(value, (int, float)) and value == value


def _as_date(value) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value)[:10]).date()
    except ValueError:
        return None


def _fresh(value, days: int) -> bool:
    stamp = _as_date(value)
    return stamp is not None and (date.today() - stamp).days <= days


def _error_status(data):
    """Return (status, message) for a CLI error payload, or None."""
    if isinstance(data, dict) and data.get("error"):
        message = str(data["error"])
        if any(marker in message for marker in TRANSIENT_MARKERS):
            return "warn", message
        return "fail", message
    return None


def check_quote(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, dict):
        return "fail", {"reason": "expected object"}
    problems = []
    if not _num(data.get("price")) or data["price"] <= 0:
        problems.append("price missing/non-positive")
    if not _num(data.get("change_pct")):
        problems.append("change_pct missing")
    if not _fresh(data.get("data_as_of") or data.get("as_of"), 10):
        problems.append(f"stale as_of={data.get('data_as_of') or data.get('as_of')}")
    if not data.get("source"):
        problems.append("source missing")
    return ("fail", {"problems": problems}) if problems else ("ok", {"source": data.get("source")})


def check_kline(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, list) or not data:
        return "fail", {"reason": "expected non-empty list"}
    last = data[-1]
    problems = []
    for field in ("date", "open", "high", "low", "close"):
        if last.get(field) is None:
            problems.append(f"last row missing {field}")
    if not _fresh(last.get("data_as_of") or last.get("date"), 10):
        problems.append(f"stale last date={last.get('date')}")
    return ("fail", {"problems": problems}) if problems else ("ok", {"rows": len(data)})


def check_indices(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, list) or len(data) < 5:
        return "fail", {"reason": "expected >=5 index rows"}
    problems = []
    for row in data:
        if not row.get("code") or not _num(row.get("price")):
            problems.append(f"bad row {row.get('code')}")
    return ("fail", {"problems": problems[:5]}) if problems else ("ok", {"rows": len(data)})


def check_market_stats(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, dict):
        return "fail", {"reason": "expected object"}
    total = data.get("total_stocks")
    up, down, flat = data.get("up_count"), data.get("down_count"), data.get("flat_count")
    problems = []
    warnings = []
    if not _num(total) or total < 1000:
        problems.append(f"total_stocks={total}")
    if not all(_num(v) for v in (up, down, flat)):
        problems.append("up/down/flat counts missing")
    elif up + down + flat > total:
        problems.append(f"breadth exceeds total: {up}+{down}+{flat} > {total}")
    elif total - (up + down + flat) > max(10, total * 0.01):
        # Suspended/newly listed rows can have no change_pct. That is a data-quality
        # warning, not a hard failure, as long as the covered rows are consistent.
        warnings.append(f"unpriced rows: {total - (up + down + flat)} of {total}")
    if not _num(data.get("total_turnover")) or data["total_turnover"] <= 0:
        problems.append("total_turnover missing")
    if problems:
        return "fail", {"problems": problems}
    if warnings:
        return "warn", {"total": total, "warnings": warnings}
    return "ok", {"total": total}


def check_fund_flow(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, list) or not data:
        return "fail", {"reason": "expected non-empty list"}
    problems = []
    if not _num(data[0].get("main_net_inflow")):
        problems.append("main_net_inflow missing")
    return ("fail", {"problems": problems}) if problems else ("ok", {"rows": len(data)})


def check_sector_flow(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, list) or len(data) < 5:
        return "fail", {"reason": "expected >=5 sector rows"}
    problems = []
    for row in data[:5]:
        if not row.get("name") or not _num(row.get("main_net_inflow")):
            problems.append(f"bad row {row.get('name')}")
    return ("fail", {"problems": problems}) if problems else ("ok", {"rows": len(data)})


def check_limit_up(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, dict):
        return "fail", {"reason": "expected object"}
    pool = data.get("pool")
    if not isinstance(pool, list):
        return "fail", {"reason": "pool missing"}
    if not _fresh(data.get("date"), 5):
        return "warn", {"reason": f"pool date={data.get('date')} (off-hours/holiday?)"}
    if not pool:
        return "warn", {"reason": "limit-up pool empty (possible non-trading day)"}
    return "ok", {"count": data.get("count")}


def check_index_valuation(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, dict):
        return "fail", {"reason": "expected object"}
    history = data.get("history") or []
    metrics = data.get("metrics") or {}
    if not history and not metrics:
        return "fail", {"reason": "no history/metrics"}
    latest = history[-1].get("date") if history else None
    if latest and not _fresh(latest, 15):
        return "warn", {"reason": f"valuation history stale ({latest})"}
    return "ok", {"history": len(history)}


def check_calendar(data) -> tuple[str, dict]:
    error = _error_status(data)
    if error:
        return error
    if not isinstance(data, dict) or "is_trading_day" not in data:
        return "fail", {"reason": "is_trading_day missing"}
    return "ok", {"is_trading_day": data["is_trading_day"]}


# (name, script, argv, validator, timeout_seconds)
CHECKS = [
    ("quote_cn", "stock_data.py", ["quote", "600519"], check_quote, 60),
    ("kline_cn", "stock_data.py", ["kline", "600519", "--count", "5"], check_kline, 60),
    ("indices_cn", "stock_data.py", ["market_indices", "--region", "cn"], check_indices, 90),
    # market_stats uses the fast efinance snapshot internally; 240s leaves room for fallbacks.
    ("market_stats", "stock_data.py", ["market_stats"], check_market_stats, 240),
    ("fund_flow_cn", "stock_data.py", ["capital_flow", "600519"], check_fund_flow, 120),
    ("sector_flow", "stock_data.py", ["capital_flow", "--mode", "sector_flow"], check_sector_flow, 120),
    ("limit_up_pool", "stock_data.py", ["limit_up_pool"], check_limit_up, 120),
    ("quote_hk", "stock_data.py", ["quote", "00700.HK"], check_quote, 60),
    ("quote_us", "stock_data.py", ["quote", "AAPL"], check_quote, 60),
    ("index_valuation", "value_data.py", ["index_valuation", "000300", "--years", "1"], check_index_valuation, 120),
    ("calendar_cn", "trading_calendar.py", ["check", "CN"], check_calendar, 60),
]


def package_versions() -> dict:
    versions = {"python": sys.version.split()[0]}
    try:
        import akshare  # noqa: PLC0415

        versions["akshare"] = getattr(akshare, "__version__", "unknown")
    except Exception:  # noqa: BLE001
        versions["akshare"] = "missing"
    try:
        import pandas  # noqa: PLC0415

        versions["pandas"] = pandas.__version__
    except Exception:  # noqa: BLE001
        versions["pandas"] = "missing"
    return versions


def _is_transient(entry: dict) -> bool:
    detail = json.dumps(entry.get("detail", {}), ensure_ascii=False)
    return any(marker in detail for marker in TRANSIENT_MARKERS)


def run_one(name: str, script: str, argv: list[str], validator, timeout: int) -> dict:
    started = time.monotonic()
    entry = {"name": name, "status": "fail", "detail": {}, "duration_s": 0.0}
    try:
        completed = subprocess.run(
            [PY, str(ROOT / "tools" / script), *argv],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            cwd=str(ROOT),
        )
    except subprocess.TimeoutExpired:
        entry.update(status="fail", detail={"reason": f"timed out after {timeout}s"})
        entry["duration_s"] = round(time.monotonic() - started, 2)
        return entry
    except Exception as exc:  # noqa: BLE001
        entry.update(status="fail", detail={"reason": f"spawn failed: {exc}"})
        entry["duration_s"] = round(time.monotonic() - started, 2)
        return entry

    raw = completed.stdout.strip()
    try:
        data = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        data = None
    if data is None:
        message = (raw or completed.stderr.strip())[:300]
        # Some CLIs print a JSON error plus non-JSON noise; try a trailing object.
        if completed.returncode != 0:
            entry.update(status="fail", detail={"reason": f"exit {completed.returncode}: {message}"})
        else:
            entry.update(status="fail", detail={"reason": f"non-JSON output: {message}"})
        entry["duration_s"] = round(time.monotonic() - started, 2)
        return entry

    status, detail = validator(data)
    entry.update(status=status, detail=detail, duration_s=round(time.monotonic() - started, 2))
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Market-data source healthcheck")
    parser.add_argument("--json", action="store_true", help="print JSON to stdout")
    parser.add_argument("--out", help="also write JSON to this path")
    parser.add_argument("--strict", action="store_true", help="warnings fail the run too")
    parser.add_argument("--only", help="comma-separated check names to run")
    args = parser.parse_args()

    selected = set(part.strip() for part in args.only.split(",") if part.strip()) if args.only else None
    started = datetime.now().astimezone()
    results = []
    for name, script, argv, validator, timeout in CHECKS:
        if selected is not None and name not in selected:
            continue
        entry = run_one(name, script, argv, validator, timeout)
        if entry["status"] == "fail" and _is_transient(entry):
            time.sleep(3)
            entry = run_one(name, script, argv, validator, timeout)
        results.append(entry)
        print(f"[{entry['status']:4}] {name:15} {entry['duration_s']:6.2f}s {entry['detail']}", file=sys.stderr)

    fails = [entry for entry in results if entry["status"] == "fail"]
    warns = [entry for entry in results if entry["status"] == "warn"]
    status = "fail" if fails or (args.strict and warns) else ("warn" if warns else "ok")
    report = {
        "status": status,
        "started_at": started.isoformat(),
        "duration_s": round((datetime.now().astimezone() - started).total_seconds(), 2),
        "versions": package_versions(),
        "summary": {
            "total": len(results),
            "ok": len(results) - len(fails) - len(warns),
            "warn": len(warns),
            "fail": len(fails),
        },
        "checks": results,
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(text)
    return 1 if status == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
