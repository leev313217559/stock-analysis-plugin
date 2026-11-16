"""Local credential file loader.

Why: DSH Desktop is a GUI process, so shell exports and `launchctl` are awkward
for per-user API tokens. Instead, every tool process loads one small env-style
file before reading credentials. Editing the file takes effect on the next tool
call (no host restart); MCP servers are long-lived and load it at startup.

Default path: ``$DSH_HOME/stock-analysis.env`` (fallback ``~/.dsh``). An
explicit ``STOCK_ANALYSIS_ENV_FILE`` overrides it for tests/CI.

File format: one ``KEY=VALUE`` per line; blank lines and full-line ``#`` comments
are ignored; an optional ``export `` prefix and matching single/double quotes are
stripped. Values are never expanded and never logged.

Real environment variables win: entries use ``os.environ.setdefault``, so
launchctl, CI, and shell settings keep precedence over the file.
"""

from __future__ import annotations

import os
import re
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import config_file

KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_loaded: set[str] = set()


def default_path() -> Path:
    return config_file().expanduser()


def _parse_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line[len("export ") :].lstrip()
    name, sep, value = line.partition("=")
    if not sep:
        return None
    name = name.strip()
    if not KEY_RE.match(name):
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return name, value


def load_credentials(path: str | Path | None = None, *, force: bool = False) -> Path | None:
    """Load credentials once per path; return the path when it exists."""
    target = Path(path).expanduser() if path is not None else default_path()
    cache_key = str(target.resolve())
    if cache_key in _loaded and not force:
        return target if target.is_file() else None
    _loaded.add(cache_key)
    if not target.is_file():
        return None
    try:
        text = target.read_text(encoding="utf-8")
    except OSError:
        return None
    # Duplicate keys: last value wins, matching the settings editor's warning.
    values: dict[str, str] = {}
    for line in text.splitlines():
        parsed = _parse_line(line)
        if parsed and parsed[1]:
            values[parsed[0]] = parsed[1]
    for name, value in values.items():
        os.environ.setdefault(name, value)
    return target


def info(path: str | Path | None = None) -> dict:
    """Non-secret metadata for diagnostics: path, existence, permission check."""
    target = Path(path).expanduser() if path is not None else default_path()
    exists = target.is_file()
    mode = None
    private = None
    if exists:
        try:
            mode = stat.S_IMODE(target.stat().st_mode)
            private = (mode & 0o077) == 0 if os.name == "posix" else True
        except OSError:
            pass
    return {
        "path": str(target),
        "exists": exists,
        "mode": oct(mode) if mode is not None else None,
        "private": private,
    }
