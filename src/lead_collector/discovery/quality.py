from dataclasses import dataclass
from urllib.parse import urlparse

from lead_collector.discovery.models import DiscoveryResult


@dataclass(frozen=True)
class QualityCheckResult:
    """Result of evaluating the quality of a discovery result."""

    accepted: bool
    reason: str


class DiscoveryQualityFilter:
    """Filter discovery results that are unlikely to represent businesses."""

    BLOCKED_DOMAINS = {
        "wikipedia.org",
        "builtin.com",
        "screener.in",
        "linkedin.com",
        "youtube.com",
        "youtu.be",
        "scribd.com",
        "naukri.com",
        "moneycontrol.com",
    }

    BLOCKED_PATH_FRAGMENTS = (
        "/articles/",
        "/article/",
        "/sharearticle",
        "/share",
        "/market/",
        "/markets/",
        "/showcase/",
        "/search/",
        "/watch",
        "/video/",
        "/videos/",
        "/guide/",
        "/guides/",
        "/list/",
    )

    BLOCKED_TITLE_PATTERNS = (
        "top ",
        "best ",
        "list of ",
        "companies in ",
        "company list",
        "software companies",
        "it companies",
        "service providers",
        "companies to know",
    )

    def check(self, result: DiscoveryResult) -> QualityCheckResult:
        """Evaluate whether a discovery result is a suitable lead source."""

        parsed = urlparse(str(result.url))
        hostname = (parsed.hostname or "").lower()
        path = parsed.path.lower()
        title = result.title.strip().lower()

        if not hostname:
            return QualityCheckResult(
                accepted=False,
                reason="missing domain",
            )

        if self._is_blocked_domain(hostname):
            return QualityCheckResult(
                accepted=False,
                reason="blocked domain",
            )

        if any(fragment in path for fragment in self.BLOCKED_PATH_FRAGMENTS):
            return QualityCheckResult(
                accepted=False,
                reason="non-business page",
            )

        if any(pattern in title for pattern in self.BLOCKED_TITLE_PATTERNS):
            return QualityCheckResult(
                accepted=False,
                reason="list or article result",
            )

        return QualityCheckResult(
            accepted=True,
            reason="accepted",
        )

    def filter(
        self,
        results: list[DiscoveryResult],
    ) -> list[DiscoveryResult]:
        """Return only discovery results that pass the quality check."""

        return [
            result
            for result in results
            if self.check(result).accepted
        ]

    def _is_blocked_domain(self, hostname: str) -> bool:
        return any(
            hostname == domain or hostname.endswith(f".{domain}")
            for domain in self.BLOCKED_DOMAINS
        )