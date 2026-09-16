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
            text=text,
            links=links,
        )