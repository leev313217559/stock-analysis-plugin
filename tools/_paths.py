"""Single source of truth for plugin-owned paths.

One root per user: `$DSH_HOME` (fallback `~/.dsh`). Configuration is a file at
the root; state lives under `stock-analysis/`:

    $DSH_HOME/stock-analysis.env      # credentials + DATA_SOURCE_PROFILE
    $DSH_HOME/stock-analysis/         # watchlist, cache, signals, reviews

Per-file overrides stay available for tests/CI (`STOCK_ANALYSIS_ENV_FILE`,
`STOCK_WATCHLIST_FILE`, `STOCK_CACHE_DIR`, `STOCK_SIGNAL_STORE`,
`STOCK_REVIEW_STORE`). There is intentionally no per-profile layout.
"""

from __future__ import annotations

import os
from pathlib import Path


def dsh_home() -> Path:
    return Path(os.environ.get("DSH_HOME") or Path.home() / ".dsh")


def data_dir() -> Path:
    return dsh_home() / "stock-analysis"


def config_file() -> Path:
    override = os.environ.get("STOCK_ANALYSIS_ENV_FILE")
    return Path(override) if override else dsh_home() / "stock-analysis.env"
