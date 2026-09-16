from dataclasses import dataclass

from lead_collector.discovery.base import LeadDiscoveryProvider
from lead_collector.extraction.exceptions import WebsiteFetchError
from lead_collector.extraction.lead_extractor import LeadExtractor
from lead_collector.extraction.parser import HTMLParser
from lead_collector.extraction.website import WebsiteFetcher
from lead_collector.models import Lead
from lead_collector.processing.deduplication import deduplicate_results
from lead_collector.processing.validation import LeadValidator
from lead_collector.storage.database import LeadDatabase


@dataclass(frozen=True)
class PipelineResult:
    """Result of a lead collection pipeline run."""

    discovered: int
    unique_results: int
    fetched: int
    failed_fetches: int
    leads: list[Lead]


class LeadCollectionPipeline:
    """Orchestrate discovery, extraction, validation, and lead creation."""

    def __init__(
        self,
        discovery_provider: LeadDiscoveryProvider,
        website_fetcher: WebsiteFetcher | None = None,
        html_parser: HTMLParser | None = None,
        lead_extractor: LeadExtractor | None = None,
        lead_validator: LeadValidator | None = None,
        database: LeadDatabase | None = None,
    ) -> None:
        self._discovery_provider = discovery_provider
        self._website_fetcher = website_fetcher or WebsiteFetcher()
        self._html_parser = html_parser or HTMLParser()
        self._lead_extractor = lead_extractor or LeadExtractor()
        self._lead_validator = lead_validator or LeadValidator()
        self._database = database

        if self._database:
            self._database.initialize()

    def run(
        self,
        query: str,
        *,
        max_results: int = 10,
    ) -> PipelineResult:
        """Run the complete lead collection pipeline."""

        discovered_results = self._discovery_provider.search(
            query,
            max_results=max_results,
        )

        unique_results = deduplicate_results(discovered_results)

        leads: list[Lead] = []
        fetched = 0
        failed_fetches = 0

        for result in unique_results:
            try:
                fetch_result = self._website_fetcher.fetch(
                    str(result.url)
                )
            except WebsiteFetchError:
                failed_fetches += 1
                continue

            fetched += 1

            page = self._html_parser.parse(
                fetch_result.content,
                base_url=fetch_result.url,
            )

            lead = self._lead_extractor.extract(
                page,
                fetch_result.url,
            )

            lead = self._lead_validator.validate(lead)

            if self._database:
                self._database.insert(lead)

            leads.append(lead)

        return PipelineResult(
            discovered=len(discovered_results),
            unique_results=len(unique_results),
            fetched=fetched,
            failed_fetches=failed_fetches,
            leads=leads,
        )