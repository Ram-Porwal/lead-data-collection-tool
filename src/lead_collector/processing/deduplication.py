from collections.abc import Iterable

from lead_collector.discovery.models import DiscoveryResult
from lead_collector.processing.normalization import normalize_url


def deduplicate_results(
    results: Iterable[DiscoveryResult],
) -> list[DiscoveryResult]:
    """Remove duplicate discovery results while preserving order."""
    unique_results: list[DiscoveryResult] = []
    seen_urls: set[str] = set()

    for result in results:
        normalized_url = normalize_url(str(result.url))

        if not normalized_url or normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        unique_results.append(result)

    return unique_results