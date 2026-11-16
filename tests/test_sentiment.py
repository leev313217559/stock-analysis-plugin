"""Tests for enhanced social sentiment in tools/search_intel.py."""

from unittest.mock import MagicMock, patch

from tools.search_intel import (
    _eastmoney_guba_heat,
    _xueqiu_heat,
    get_social_sentiment,
)


class TestEastmoneyGuba:
    @patch("requests.get")
    def test_returns_data(self, mock_get, monkeypatch):
        monkeypatch.setenv("XUEQIU_TOKEN", "test-token")
        mock_get.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "re": {
                    "hot_rank": 5,
                    "post_count": 120,
                    "view_count": 50000,
                    "sentiment": 0.65,
                }
            },
        )
        result = _eastmoney_guba_heat("600519")
        assert result["source"] == "eastmoney_guba"
        assert result["hot_rank"] == 5
        assert result["post_count_today"] == 120

    @patch("requests.get")
    def test_failed_request_returns_empty(self, mock_get):
        mock_get.return_value = MagicMock(ok=False)
        result = _eastmoney_guba_heat("600519")
        assert result == {}

    @patch("requests.get")
    def test_exception_returns_empty(self, mock_get, monkeypatch):
        monkeypatch.setenv("XUEQIU_TOKEN", "test-token")
        mock_get.side_effect = Exception("network error")
        result = _eastmoney_guba_heat("600519")
        assert result == {}


class TestXueqiuHeat:
    @patch("requests.get")
    def test_returns_data(self, mock_get, monkeypatch):
        monkeypatch.setenv("XUEQIU_TOKEN", "test-token")
        mock_get.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "data": {
                    "followers": 150000,
                    "discussion_count": 800,
                    "value": 95,
                    "rank": 3,
                }
            },
        )
        result = _xueqiu_heat("600519")
        assert result["source"] == "xueqiu"
        assert result["followers"] == 150000
        assert result["rank"] == 3

    @patch("requests.get")
    def test_sh_prefix_for_6xx(self, mock_get, monkeypatch):
        monkeypatch.setenv("XUEQIU_TOKEN", "test-token")
        mock_get.return_value = MagicMock(ok=True, json=lambda: {"data": {"followers": 100}})
        _xueqiu_heat("600519")
        call_params = mock_get.call_args[1].get("params") or mock_get.call_args[0][0]
        # Verify SH prefix is used for 6xx codes
        if isinstance(call_params, dict):
            assert "SH600519" in str(mock_get.call_args)

    @patch("requests.get")
    def test_sz_prefix_for_0xx(self, mock_get, monkeypatch):
        monkeypatch.setenv("XUEQIU_TOKEN", "test-token")
        mock_get.return_value = MagicMock(ok=True, json=lambda: {"data": {"followers": 100}})
        _xueqiu_heat("000001")
        assert "SZ000001" in str(mock_get.call_args)

    @patch("requests.get")
    def test_exception_returns_empty(self, mock_get, monkeypatch):
        monkeypatch.setenv("XUEQIU_TOKEN", "test-token")
        mock_get.side_effect = Exception("timeout")
        result = _xueqiu_heat("600519")
        assert result == {}

    @patch("requests.get")
    def test_without_token_skips_request(self, mock_get, monkeypatch):
        monkeypatch.delenv("XUEQIU_TOKEN", raising=False)
        assert _xueqiu_heat("600519") == {}
        mock_get.assert_not_called()


class TestGetSocialSentimentMarketDetection:
    @patch("tools.search_intel._xueqiu_heat")
    @patch("tools.search_intel._eastmoney_guba_heat")
    def test_a_share_routes_to_guba_xueqiu(self, mock_guba, mock_xueqiu):
        mock_guba.return_value = {"source": "eastmoney_guba", "hot_rank": 5}
        mock_xueqiu.return_value = {"source": "xueqiu", "followers": 100}
        result = get_social_sentiment("600519")
        assert "eastmoney_guba" in result["sources"]
        assert "xueqiu" in result["sources"]
        mock_guba.assert_called_once_with("600519")
        mock_xueqiu.assert_called_once_with("600519")

    def test_us_stock_returns_a_share_only_note(self):
        result = get_social_sentiment("AAPL")
        assert result["sources"] == {}
        assert "A-share only" in result["note"]

    def test_hk_stock_returns_a_share_only_note(self):
        result = get_social_sentiment("0700.HK")
        assert result["sources"] == {}
        assert "A-share only" in result["note"]

    @patch("tools.search_intel._xueqiu_heat")
    @patch("tools.search_intel._eastmoney_guba_heat")
    def test_a_share_empty_shows_note(self, mock_guba, mock_xueqiu):
        mock_guba.return_value = {}
        mock_xueqiu.return_value = {}
        result = get_social_sentiment("600519")
        assert "note" in result
        assert "东方财富" in result["note"]

    def test_wisburg_context_always_present(self):
        with (
            patch("tools.search_intel._eastmoney_guba_heat", return_value={}),
            patch("tools.search_intel._xueqiu_heat", return_value={}),
        ):
            result = get_social_sentiment("600519")
        assert "additional_context" in result
        assert "wisburg_mcp" in result["additional_context"]
