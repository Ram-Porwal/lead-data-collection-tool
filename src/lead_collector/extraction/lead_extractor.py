from urllib.parse import urlparse

from lead_collector.extraction.fields import (
    extract_emails,
    extract_linkedin_url,
    extract_phone_numbers,
)
from lead_collector.extraction.parser import ParsedPage
from lead_collector.models import Lead


class LeadExtractor:
    """Convert parsed webpage information into Lead objects."""

    def extract(self, page: ParsedPage, source_url: str) -> Lead:
        """Extract a Lead from a parsed webpage."""

        emails = extract_emails(page.text)
        phone_numbers = extract_phone_numbers(page.text)
        linkedin_url = extract_linkedin_url(page.links)

        company_name = self._extract_company_name(page.title, source_url)

        return Lead(
            company_name=company_name,
            website=source_url,
            email=emails[0] if emails else None,
            phone=phone_numbers[0] if phone_numbers else None,
            linkedin_url=linkedin_url,
            source_url=source_url,
        )

    @staticmethod
    def _extract_company_name(
        title: str | None,
        source_url: str,
    ) -> str:
        """Determine a reasonable company name."""

        if title:
            return title

        hostname = urlparse(source_url).hostname

        if hostname:
            hostname = hostname.removeprefix("www.")
            return hostname.split(".")[0].replace("-", " ").title()

        return "Unknown Company"