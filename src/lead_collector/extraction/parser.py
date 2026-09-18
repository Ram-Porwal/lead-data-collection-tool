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
    organization_industry: str | None = None
    organization_email: str | None = None
    organization_telephone: str | None = None
    organization_city: str | None = None
    organization_state: str | None = None
    organization_country: str | None = None


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

        organization = self._extract_organization(soup)

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
            organization_name=organization["name"],
            organization_industry=organization["industry"],
            organization_email=organization["email"],
            organization_telephone=organization["telephone"],
            organization_city=organization["city"],
            organization_state=organization["state"],
            organization_country=organization["country"],
            text=text,
            links=links,
        )

    @staticmethod
    def _extract_organization(
        soup: BeautifulSoup,
    ) -> dict[str, str | None]:
        """Extract structured Organization metadata from JSON-LD."""

        result: dict[str, str | None] = {
            "name": None,
            "industry": None,
            "email": None,
            "telephone": None,
            "city": None,
            "state": None,
            "country": None,
        }

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

                if candidate.get("@type") != "Organization":
                    continue

                result.update(
                    HTMLParser._organization_fields(candidate)
                )

                # We have found an actual Organization object.
                # Continue searching only for missing fields.
                if all(
                    value is not None
                    for value in result.values()
                ):
                    return result

        return result

    @staticmethod
    def _organization_fields(
        organization: dict,
    ) -> dict[str, str | None]:
        """Normalize fields from one JSON-LD Organization object."""

        fields: dict[str, str | None] = {
            "name": HTMLParser._clean_string(
                organization.get("name")
            ),
            "industry": HTMLParser._clean_string(
                organization.get("industry")
            ),
            "email": HTMLParser._clean_string(
                organization.get("email")
            ),
            "telephone": HTMLParser._clean_string(
                organization.get("telephone")
            ),
            "city": None,
            "state": None,
            "country": None,
        }

        address = organization.get("address")

        if isinstance(address, dict):
            fields["city"] = HTMLParser._clean_string(
                address.get("addressLocality")
            )
            fields["state"] = HTMLParser._clean_string(
                address.get("addressRegion")
            )
            fields["country"] = HTMLParser._clean_string(
                address.get("addressCountry")
            )

            # Schema.org sometimes represents addressCountry as an object.
            if isinstance(address.get("addressCountry"), dict):
                fields["country"] = HTMLParser._clean_string(
                    address["addressCountry"].get("name")
                )

        return fields

    @staticmethod
    def _clean_string(value: object) -> str | None:
        """Return a normalized non-empty string or None."""

        if isinstance(value, str) and value.strip():
            return value.strip()

        return None