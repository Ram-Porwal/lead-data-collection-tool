from dataclasses import dataclass

import requests

from lead_collector.extraction.exceptions import WebsiteFetchError


@dataclass(frozen=True)
class FetchResult:
    """Result of fetching a webpage."""

    url: str
    status_code: int
    content: str


class WebsiteFetcher:
    """Fetch public webpages with safe request defaults."""

    def __init__(
        self,
        *,
        timeout: float = 10.0,
        user_agent: str = "LeadDataCollectionTool/0.1",
    ) -> None:
        self._timeout = timeout
        self._headers = {"User-Agent": user_agent}

    def fetch(self, url: str) -> FetchResult:
        """Fetch a webpage and return its response content."""
        try:
            response = requests.get(
                url,
                headers=self._headers,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise WebsiteFetchError("Website fetch failed.") from exc

        return FetchResult(
            url=url,
            status_code=response.status_code,
            content=response.text,
        )