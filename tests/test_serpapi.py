from unittest.mock import MagicMock

import pytest
import requests
import serpapi

from lead_collector.config import Settings
from lead_collector.discovery.serpapi import SerpApiDiscoveryProvider
from lead_collector.discovery.exceptions import DiscoveryProviderError


@pytest.fixture
def provider():
    settings = Settings(serpapi_key="test-api-key")
    return SerpApiDiscoveryProvider(settings)


def test_search_returns_discovery_results(provider):
    provider._client = MagicMock()
    provider._client.search.return_value = {
        "organic_results": [
            {
                "title": "Example Company",
                "link": "https://example.com",
                "snippet": "Example company website",
                "position": 1,
            },
            {
                "title": "Another Company",
                "link": "https://another.example.com",
                "snippet": "Another company website",
                "position": 2,
            },
        ]
    }

    results = provider.search("software companies", max_results=2)

    assert len(results) == 2
    assert results[0].title == "Example Company"
    assert str(results[0].url) == "https://example.com/"
    assert results[0].source == "serpapi"
    assert results[0].position == 1


def test_search_respects_max_results(provider):
    provider._client = MagicMock()
    provider._client.search.return_value = {
        "organic_results": [
            {
                "title": f"Company {i}",
                "link": f"https://example{i}.com",
                "position": i,
            }
            for i in range(1, 6)
        ]
    }

    results = provider.search("companies", max_results=2)

    assert len(results) == 2


def test_search_returns_empty_for_zero_max_results(provider):
    provider._client = MagicMock()

    results = provider.search("companies", max_results=0)

    assert results == []
    provider._client.search.assert_not_called()


def test_search_skips_results_missing_title_or_link(provider):
    provider._client = MagicMock()
    provider._client.search.return_value = {
        "organic_results": [
            {
                "title": "Valid Company",
                "link": "https://valid.example.com",
            },
            {
                "title": "Missing Link",
            },
            {
                "link": "https://missing-title.example.com",
            },
        ]
    }

    results = provider.search("companies", max_results=10)

    assert len(results) == 1
    assert results[0].title == "Valid Company"


def test_search_raises_provider_error_on_http_failure(provider):
    provider._client = MagicMock()

    response = requests.Response()
    response.status_code = 401

    original_error = requests.exceptions.HTTPError(
        "Authentication failed",
        response=response,
    )

    provider._client.search.side_effect = serpapi.HTTPError(original_error)

    with pytest.raises(DiscoveryProviderError, match="SerpApi search failed."):
        provider.search("companies")


def test_search_raises_provider_error_on_timeout(provider):
    provider._client = MagicMock()
    provider._client.search.side_effect = serpapi.TimeoutError(
        "Request timed out"
    )

    with pytest.raises(DiscoveryProviderError, match="SerpApi search failed."):
        provider.search("companies")