import json
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ParsedPage:
    """Structured information extracted from an HTML page."""

    title: str | None
    description: str | None
    text: str
    links: list[str]
    site_name: str | None = None
    canonical_url: str | None = None
    organization_name: str | None = None


class HTMLParser:
    """Parse useful information from public HTML pages."""

    def parse(self, html: str, base_url: str | None = None) -> ParsedPage:
        """Parse HTML into structured page information."""
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.get_text(strip=True) if soup.title else None

        description_tag = soup.find(
            "meta",
            attrs={"name": "description"},
        )
        description = (
            description_tag.get("content", "").strip()
            if description_tag
            else None
        )

        site_name_tag = soup.find(
            "meta",
            attrs={"property": "og:site_name"},
        )
        site_name = (
            site_name_tag.get("content", "").strip()
            if site_name_tag
            else None
        )

        canonical_tag = soup.find(
            "link",
            attrs={"rel": lambda value: value and "canonical" in value},
        )

        canonical_url = None

        if canonical_tag:
            href = canonical_tag.get("href", "").strip()

            if href:
                canonical_url = (
                    urljoin(base_url, href)
                    if base_url
                    else href
                )

        organization_name = self._extract_organization_name(soup)

        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        text = soup.get_text(" ", strip=True)

        links: list[str] = []

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()

            if not href:
                continue

            if base_url:
                href = urljoin(base_url, href)

            links.append(href)

        return ParsedPage(
            title=title,
            description=description,
            site_name=site_name,
            canonical_url=canonical_url,
            organization_name=organization_name,
            text=text,
            links=links,
        )

    @staticmethod
    def _extract_organization_name(
        soup: BeautifulSoup,
    ) -> str | None:
        """Extract an Organization name from JSON-LD metadata."""

        for script in soup.find_all(
            "script",
            attrs={"type": "application/ld+json"},
        ):
            raw_json = script.string

            if not raw_json:
                continue

            try:
                data = json.loads(raw_json)
            except (json.JSONDecodeError, TypeError):
                continue

            candidates = data if isinstance(data, list) else [data]

            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue

                if candidate.get("@type") == "Organization":
                    name = candidate.get("name")

                    if isinstance(name, str) and name.strip():
                        return name.strip()

        return None