from pathlib import Path
from dataclasses import dataclass

from lead_collector.export.csv_exporter import CSVLeadExporter
from lead_collector.export.excel_exporter import ExcelLeadExporter
from lead_collector.discovery.base import LeadDiscoveryProvider
from lead_collector.discovery.quality import DiscoveryQualityFilter
from lead_collector.extraction.exceptions import WebsiteFetchError
from lead_collector.extraction.lead_extractor import LeadExtractor
from lead_collector.extraction.parser import HTMLParser
from lead_collector.extraction.website import WebsiteFetcher
from lead_collector.models import Lead
from lead_collector.processing.deduplication import deduplicate_results
from lead_collector.processing.lead_deduplication import deduplicate_leads
from lead_collector.processing.validation import LeadValidator
from lead_collector.reporting.summary import PipelineSummary
from lead_collector.storage.database import LeadDatabase


@dataclass(frozen=True)
class PipelineResult:
    """Result of a lead collection pipeline run."""

    discovered: int
    rejected_by_quality: int
    unique_results: int
    fetched: int
    failed_fetches: int
    challenge_pages: int
    lead_duplicates: int
    valid_leads: int
    invalid_leads: int
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
        csv_exporter: CSVLeadExporter | None = None,
        excel_exporter: ExcelLeadExporter | None = None,
        ) -> None:
        self._discovery_provider = discovery_provider
        self._quality_filter = DiscoveryQualityFilter()
        self._website_fetcher = website_fetcher or WebsiteFetcher()
        self._html_parser = html_parser or HTMLParser()
        self._lead_extractor = lead_extractor or LeadExtractor()
        self._lead_validator = lead_validator or LeadValidator()
        self._database = database
        self._csv_exporter = csv_exporter
        self._excel_exporter = excel_exporter

        if self._database:
            self._database.initialize()

    def run(
        self,
        query: str,
        *,
        max_results: int = 10,
        csv_path: str | Path | None = None,
        excel_path: str | Path | None = None,
    ) -> PipelineResult:
        """Run the complete lead collection pipeline."""

        discovered_results = self._discovery_provider.search(
            query,
            max_results=max_results,
        )

        quality_results = self._quality_filter.filter(
            discovered_results
        )

        unique_results = deduplicate_results(quality_results)

        leads: list[Lead] = []
        fetched = 0
        failed_fetches = 0
        challenge_pages = 0

        for result in unique_results:
            try:
                fetch_result = self._website_fetcher.fetch(
                    str(result.url)
                )
            except WebsiteFetchError:   
                failed_fetches += 1
                continue

            fetched += 1

            if fetch_result.is_challenge_page:
                challenge_pages += 1
                continue

            page = self._html_parser.parse(
                fetch_result.content,
                base_url=fetch_result.url,
            )

            lead = self._lead_extractor.extract(
                page,
                fetch_result.url,
            )

            lead = self._lead_validator.validate(lead)

            leads.append(lead)

        extracted_leads = len(leads)

        leads = deduplicate_leads(leads)

        lead_duplicates = extracted_leads - len(leads)

        valid_leads = sum(
            lead.validation_status.value == "valid"
            for lead in leads
        )

        invalid_leads = sum(
            lead.validation_status.value == "invalid"
            for lead in leads
        )

        for lead in leads:
            if self._database:
                self._database.insert(lead)

        if self._csv_exporter and csv_path:
            self._csv_exporter.export(leads, csv_path)

        rejected_by_quality = len(discovered_results) - len(quality_results)

        result = PipelineResult(
            discovered=len(discovered_results),
            rejected_by_quality=rejected_by_quality,
            unique_results=len(unique_results),
            fetched=fetched,
            failed_fetches=failed_fetches,
            challenge_pages=challenge_pages,
            lead_duplicates=lead_duplicates,
            valid_leads=valid_leads,
            invalid_leads=invalid_leads,
            leads=leads,
        )

        if self._excel_exporter and excel_path:
            summary = PipelineSummary.from_result(result)
            self._excel_exporter.export(
                leads,
                excel_path,
                summary=summary,
            )

        return result