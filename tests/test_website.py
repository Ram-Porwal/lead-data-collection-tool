from unittest.mock import MagicMock, patch

import pytest
import requests

from lead_collector.extraction.website import WebsiteFetcher
from lead_collector.extraction.exceptions import WebsiteFetchError


def test_fetch_returns_fetch_result():
    response = MagicMock()
    response.status_code = 200
    response.text = "<html><body>Hello</body></html>"

    with patch(
        "lead_collector.extraction.website.requests.get",
        return_value=response,
    ) as mock_get:
        fetcher = WebsiteFetcher(timeout=5.0)

        result = fetcher.fetch("https://example.com")

    mock_get.assert_called_once_with(
        "https://example.com",
        headers={"User-Agent": "LeadDataCollectionTool/0.1"},
        timeout=5.0,
    )

    assert result.url == "https://example.com"
    assert result.status_code == 200
    assert result.content == "<html><body>Hello</body></html>"


def test_fetch_raises_for_http_error():
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("404")

    with patch(
        "lead_collector.extraction.website.requests.get",
        return_value=response,
    ):
        fetcher = WebsiteFetcher()

        with pytest.raises(WebsiteFetchError):
            fetcher.fetch("https://example.com/missing")


def test_fetch_uses_custom_user_agent():
    response = MagicMock()
    response.status_code = 200
    response.text = "OK"

    with patch(
        "lead_collector.extraction.website.requests.get",
        return_value=response,
    ) as mock_get:
        fetcher = WebsiteFetcher(user_agent="TestBot/1.0")
        fetcher.fetch("https://example.com")

    mock_get.assert_called_once_with(
        "https://example.com",
        headers={"User-Agent": "TestBot/1.0"},
        timeout=10.0,
    )


def test_fetch_detects_challenge_page():
    response = MagicMock()
    response.status_code = 200
    response.text = """
    <html>
        <head><title>Radware Captcha Page</title></head>
        <body>
            Please complete the CAPTCHA to continue.
        </body>
    </html>
    """

    with patch(
        "lead_collector.extraction.website.requests.get",
        return_value=response,
    ):
        fetcher = WebsiteFetcher()

        result = fetcher.fetch("https://example.com")

    assert result.is_challenge_page is True


def test_fetch_does_not_misclassify_normal_page_that_mentions_captcha():
    response = MagicMock()
    response.status_code = 200
    response.text = """
    <html>
        <head><title>Example Company</title></head>
        <body>
            Our security policy explains how CAPTCHA helps prevent abuse.
            Contact us at support@example.com.
        </body>
    </html>
    """

    with patch(
        "lead_collector.extraction.website.requests.get",
        return_value=response,
    ):
        fetcher = WebsiteFetcher()

        result = fetcher.fetch("https://example.com")

    assert result.is_challenge_page is False


def test_fetch_detects_human_verification_page():
    response = MagicMock()
    response.status_code = 200
    response.text = """
    <html>
        <head><title>Security Check</title></head>
        <body>
            Verify you are human before continuing.
        </body>
    </html>
    """

    with patch(
        "lead_collector.extraction.website.requests.get",
        return_value=response,
    ):
        fetcher = WebsiteFetcher()

        result = fetcher.fetch("https://example.com")

    assert result.is_challenge_page is True