"""One-root path resolution for config and plugin state."""

from pathlib import Path

from tools import _paths


def test_dsh_home_drives_config_and_state(monkeypatch):
    monkeypatch.setenv("DSH_HOME", "/tmp/dsh-home-test")
    monkeypatch.delenv("STOCK_ANALYSIS_ENV_FILE", raising=False)
    assert _paths.dsh_home() == Path("/tmp/dsh-home-test")
    assert _paths.data_dir() == Path("/tmp/dsh-home-test/stock-analysis")
    assert _paths.config_file() == Path("/tmp/dsh-home-test/stock-analysis.env")


def test_explicit_config_override(monkeypatch):
    monkeypatch.setenv("STOCK_ANALYSIS_ENV_FILE", "/tmp/custom.env")
    assert _paths.config_file() == Path("/tmp/custom.env")
