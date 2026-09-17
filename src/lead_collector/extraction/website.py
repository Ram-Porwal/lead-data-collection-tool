from dataclasses import dataclass

import requests

from lead_collector.extraction.exceptions import WebsiteFetchError


@dataclass(frozen=True)
class FetchResult:
    """Result of fetching a webpage."""

    url: str
    status_code: int
    content: str
    is_challenge_page: bool = False


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
            is_challenge_page=self._is_challenge_page(response.text),
        )

    @staticmethod
    def _is_challenge_page(content: str) -> bool:
        """Detect common CAPTCHA or browser challenge pages."""

        content_lower = content.lower()

        strong_indicators = (
            "radware captcha page",
            "please complete the captcha",
            "verify you are human",
            "human verification",
            "security verification",
            "checking your browser",
            "challenge page",
        )

        return any(
            indicator in content_lower
            for indicator in strong_indicators
        )