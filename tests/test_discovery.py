import pytest
from pydantic import ValidationError

from lead_collector.discovery.models import DiscoveryResult
from lead_collector.discovery.base import LeadDiscoveryProvider



def test_valid_discovery_result():
    result = DiscoveryResult(
        title="ABC Technologies",
        url="https://example.com",
        snippet="Software company in Ahmedabad",
        source="serpapi",
        position=1,
    )

    assert result.title == "ABC Technologies"
    assert str(result.url) == "https://example.com/"
    assert result.source == "serpapi"
    assert result.position == 1


def test_invalid_discovery_url():
    with pytest.raises(ValidationError):
        DiscoveryResult(
            title="ABC Technologies",
            url="not-a-url",
            source="serpapi",
        )


def test_optional_fields_can_be_missing():
    result = DiscoveryResult(
        title="ABC Technologies",
        url="https://example.com",
        source="serpapi",
    )

    assert result.snippet is None
    assert result.position is None


class FakeDiscoveryProvider(LeadDiscoveryProvider):
    """Test provider used to verify the discovery interface."""

    def search(
        self,
        query: str,
        *,
        max_results: int = 10,
    ) -> list[DiscoveryResult]:
        return [
            DiscoveryResult(
                title="ABC Technologies",
                url="https://example.com",
                snippet=f"Result for: {query}",
                source="fake",
                position=1,
            )
        ][:max_results]


def test_discovery_provider_returns_results():
    provider = FakeDiscoveryProvider()

    results = provider.search("software companies in Ahmedabad")

    assert len(results) == 1
    assert results[0].title == "ABC Technologies"
    assert results[0].source == "fake"


def test_discovery_provider_respects_max_results():
    provider = FakeDiscoveryProvider()

    results = provider.search(
        "software companies in Ahmedabad",
        max_results=0,
    )

    assert results == []