"""Data-source profiles.

Capability code keeps its declared failover chain; this module decides which legs
a profile actually runs. ``lean`` (default) keeps 2-3 keyless, best-maintained
providers per capability. ``full`` restores the upstream multi-fallback behavior
(every declared leg, in declared order).

Profiles are selected by ``DATA_SOURCE_PROFILE`` (``lean`` | ``full``). Unknown
values fall back to ``lean``. A profile never removes every leg: if a filter
would empty a chain, the declared chain is returned unchanged so a capability
degrades to "try what exists" instead of "no source at all".
"""

from __future__ import annotations

import os

PROFILE_ENV = "DATA_SOURCE_PROFILE"
DEFAULT_PROFILE = "lean"

# capability -> ordered provider names to keep in the lean profile.
LEAN = {
    # A-share quotes / klines (keyless first, akshare kept for qfq).
    "quote_a": ["tencent", "sina"],
    "quote_a_etf": ["tencent", "akshare_etf", "sina"],
    "kline_a": ["tencent", "sina", "akshare"],
    # Full-market snapshot: eastmoney is the richest, sina/tencent are keyless backstops.
    "snapshot_a": ["akshare", "sina", "tencent"],
    # Boards.
    "sector_rankings": ["eastmoney", "ths", "sina"],
    "sector_constituents": ["eastmoney_industry", "eastmoney_concept", "sina"],
    # Fund flows: eastmoney primary, efinance is the keyless backstop that saved
    # individual flow when eastmoney rate-limited the shared runner IP.
    "fund_flow": ["eastmoney", "efinance"],
    "dragon_tiger": ["eastmoney", "sina"],
    "hot_stocks": ["eastmoney"],
    "margin_kline": ["akshare", "efinance"],
    # HK/US quotes and klines: keyless Tencent first, yfinance as the global backstop.
    "yf_quote_hk": ["tencent", "yfinance"],
    "yf_kline_hk": ["tencent", "yfinance"],
    "yf_quote_us": ["tencent", "yfinance"],
    "yf_kline_us": ["tencent", "yfinance"],
    "yf_quote_other": ["yfinance"],
    "yf_kline_other": ["yfinance"],
}

# Chain label (before ":") -> capability key. Unknown labels keep their chain.
LABEL_CAPABILITIES = {
    "quote_a": "quote_a",
    "quote_a_etf": "quote_a_etf",
    "kline_a": "kline_a",
    "snapshot_a": "snapshot_a",
    "sector_rankings": "sector_rankings",
    "sector_constituents": "sector_constituents",
    "dragon_tiger": "dragon_tiger",
    "hot_stocks": "hot_stocks",
    "margin_turnover": "margin_kline",
}


def active_profile() -> str:
    value = os.environ.get(PROFILE_ENV, DEFAULT_PROFILE).strip().lower()
    return value if value in ("lean", "full") else DEFAULT_PROFILE


def select(capability: str, sources: list) -> list:
    """Filter/reorder one capability's chain for the active profile."""
    if active_profile() == "full":
        return sources
    order = LEAN.get(capability)
    if not order:
        return sources
    by_name = {}
    for leg in sources:
        name = leg[0]
        if name not in by_name:
            by_name[name] = leg
    selected = [by_name[name] for name in order if name in by_name]
    # Never hand _failover an empty chain: fall back to the declared legs.
    return selected or sources


def select_for_label(label: str, sources: list) -> list:
    """Apply the profile using a _failover label such as ``quote_a:600519``."""
    capability = LABEL_CAPABILITIES.get(label.split(":", 1)[0])
    return select(capability, sources) if capability else sources
