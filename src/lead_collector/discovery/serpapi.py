import serpapi

from lead_collector.config import Settings
from lead_collector.discovery.base import LeadDiscoveryProvider
from lead_collector.discovery.exceptions import DiscoveryProviderError
from lead_collector.discovery.models import DiscoveryResult


class SerpApiDiscoveryProvider(LeadDiscoveryProvider):
    """Lead discovery provider backed by SerpApi."""

    def __init__(self, settings: Settings) -> None:
        self._client = serpapi.Client(api_key=settings.serpapi_key)

    def search(
        self,
        query: str,
        *,
        max_results: int = 10,
    ) -> list[DiscoveryResult]:
        if max_results <= 0:
            return []

        try:
            response = self._client.search(
                {
                    "engine": "google",
                    "q": query,
                    "num": max_results,
                }
            )
        except (serpapi.HTTPError, serpapi.TimeoutError) as exc:
            raise DiscoveryProviderError(
                "SerpApi search failed."
            ) from exc

        organic_results = response.get("organic_results", [])

        return [
            DiscoveryResult(
                title=result["title"],
                url=result["link"],
                snippet=result.get("snippet"),
                source="serpapi",
                position=result.get("position"),
            )
            for result in organic_results[:max_results]
            if result.get("title") and result.get("link")
        ]