"""Credential-file loading: parsing, precedence, isolation, and secrecy."""

import os
from pathlib import Path

import pytest

from tools import _credentials


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "creds.env"
    path.write_text(text, encoding="utf-8")
    return path


def test_loads_values_comments_quotes_and_export(tmp_path, monkeypatch):
    for key in ("SA_TEST_A", "SA_TEST_B", "SA_TEST_C"):
        monkeypatch.delenv(key, raising=False)
    path = _write(
        tmp_path,
        """
# full-line comment
SA_TEST_A=alpha
export SA_TEST_B="beta gamma"
SA_TEST_C='delta'
""",
    )
    assert _credentials.load_credentials(path, force=True) == path
    assert os.environ["SA_TEST_A"] == "alpha"
    assert os.environ["SA_TEST_B"] == "beta gamma"
    assert os.environ["SA_TEST_C"] == "delta"


def test_real_environment_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("SA_TEST_PRECEDENCE", "from-env")
    path = _write(tmp_path, "SA_TEST_PRECEDENCE=from-file\n")
    assert _credentials.load_credentials(path, force=True) == path
    assert os.environ["SA_TEST_PRECEDENCE"] == "from-env"


def test_duplicate_keys_last_wins(tmp_path, monkeypatch):
    monkeypatch.delenv("SA_TEST_DUP", raising=False)
    path = _write(tmp_path, "SA_TEST_DUP=first\nSA_TEST_DUP=second\n")
    assert _credentials.load_credentials(path, force=True) == path
    assert os.environ["SA_TEST_DUP"] == "second"


def test_invalid_lines_are_ignored(tmp_path, monkeypatch):
    monkeypatch.delenv("SA_TEST_OK", raising=False)
    path = _write(
        tmp_path,
        """
not a pair
=missing-name
1BAD=value
SA_TEST_OK=yes
""",
    )
    assert _credentials.load_credentials(path, force=True) == path
    assert os.environ["SA_TEST_OK"] == "yes"


def test_missing_file_is_a_noop(tmp_path):
    assert _credentials.load_credentials(tmp_path / "absent.env", force=True) is None


def test_explicit_override_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("STOCK_ANALYSIS_ENV_FILE", str(tmp_path / "custom.env"))
    assert _credentials.default_path() == tmp_path / "custom.env"


def test_dsh_home_is_used(monkeypatch):
    monkeypatch.delenv("STOCK_ANALYSIS_ENV_FILE", raising=False)
    monkeypatch.setenv("DSH_HOME", "/tmp/dsh-home-test")
    assert _credentials.default_path() == Path("/tmp/dsh-home-test/stock-analysis.env")


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
def test_info_reports_private_permissions(tmp_path):
    path = _write(tmp_path, "A=1\n")
    path.chmod(0o600)
    assert _credentials.info(path)["private"] is True
    path.chmod(0o644)
    assert _credentials.info(path)["private"] is False


def test_utf8_stdio_loads_the_file(monkeypatch, tmp_path):
    monkeypatch.delenv("SA_TEST_STDIO", raising=False)
    path = _write(tmp_path, "SA_TEST_STDIO=loaded\n")
    monkeypatch.setenv("STOCK_ANALYSIS_ENV_FILE", str(path))
    from tools._subproc import utf8_stdio

    utf8_stdio()
    assert os.environ["SA_TEST_STDIO"] == "loaded"


def test_values_are_not_printed(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("SA_TEST_SECRET", raising=False)
    path = _write(tmp_path, "SA_TEST_SECRET=super-secret-value\n")
    _credentials.load_credentials(path, force=True)
    captured = capsys.readouterr()
    assert "super-secret-value" not in captured.out
    assert "super-secret-value" not in captured.err
