from unittest.mock import MagicMock

from lead_collector.discovery.models import DiscoveryResult
from lead_collector.extraction.website import FetchResult
from lead_collector.extraction.exceptions import WebsiteFetchError
from lead_collector.models import ValidationStatus
from lead_collector.pipeline import LeadCollectionPipeline


def make_result(
    url: str,
    position: int = 1,
) -> DiscoveryResult:
    return DiscoveryResult(
        title="Example Company",
        url=url,
        snippet="Example company website",
        source="test",
        position=position,
    )


def test_pipeline_counts_challenge_pages():
    discovery = MagicMock()

    discovery.search.return_value = [
        make_result("https://challenge.example"),
        make_result("https://working.example"),
    ]

    fetcher = MagicMock()

    fetcher.fetch.side_effect = [
        FetchResult(
            url="https://challenge.example",
            status_code=403,
            content="<html>Challenge</html>",
            is_challenge_page=True,
        ),
        FetchResult(
            url="https://working.example",
            status_code=200,
            content="""
                <html>
                    <head>
                        <title>Working Company</title>
                    </head>
                    <body>
                        Contact sales@working.example
                    </body>
                </html>
            """,
        ),
    ]

    pipeline = LeadCollectionPipeline(
        discovery_provider=discovery,
        website_fetcher=fetcher,
    )

    result = pipeline.run("software companies")

    assert result.fetched == 2
    assert result.challenge_pages == 1
    assert len(result.leads) == 1


def test_pipeline_counts_lead_duplicates():
    discovery = MagicMock()

    discovery.search.return_value = [
        make_result("https://first.example"),
        make_result("https://second.example"),
    ]

    fetcher = MagicMock()

    fetcher.fetch.side_effect = [
        FetchResult(
            url="https://first.example",
            status_code=200,
            content="""
                <html>
                    <head>
                        <title>Company One</title>
                    </head>
                    <body>
                        Contact sales@example.com
                    </body>
                </html>
            """,
        ),
        FetchResult(
            url="https://second.example",
            status_code=200,
            content="""
                <html>
                    <head>
                        <title>Company One Duplicate</title>
                    </head>
                    <body>
                        Contact SALES@example.com
                    </body>
                </html>
            """,
        ),
    ]

    pipeline = LeadCollectionPipeline(
        discovery_provider=discovery,
        website_fetcher=fetcher,
    )

    result = pipeline.run("software companies")

    assert len(result.leads) == 1
    assert result.lead_duplicates == 1


def test_pipeline_reports_valid_and_invalid_leads():
    discovery = MagicMock()

    discovery.search.return_value = [
        make_result("https://valid.example"),
        make_result("https://invalid.example"),
    ]

    fetcher = MagicMock()

    fetcher.fetch.side_effect = [
        FetchResult(
            url="https://valid.example",
            status_code=200,
            content="""
                <html>
                    <head>
                        <title>Valid Company</title>
                    </head>
                    <body>
                        Contact sales@valid.example
                    </body>
                </html>
            """,
        ),
        FetchResult(
            url="https://invalid.example",
            status_code=200,
            content="""
                <html>
                    <head>
                        <title>Invalid Company</title>
                    </head>
                    <body>
                        No contact information available.
                    </body>
                </html>
            """,
        ),
    ]

    pipeline = LeadCollectionPipeline(
        discovery_provider=discovery,
        website_fetcher=fetcher,
    )

    result = pipeline.run("software companies")

    assert len(result.leads) == 2

    assert result.valid_leads == 1
    assert result.invalid_leads == 1


def test_pipeline_observability_counts_zero_for_empty_run():
    discovery = MagicMock()
    discovery.search.return_value = []

    fetcher = MagicMock()

    pipeline = LeadCollectionPipeline(
        discovery_provider=discovery,
        website_fetcher=fetcher,
    )

    result = pipeline.run("software companies")

    assert result.challenge_pages == 0
    assert result.lead_duplicates == 0
    assert result.valid_leads == 0
    assert result.invalid_leads == 0