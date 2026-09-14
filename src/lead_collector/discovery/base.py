from abc import ABC, abstractmethod

from .models import DiscoveryResult


class LeadDiscoveryProvider(ABC):
    """Interface for lead discovery providers."""

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        max_results: int = 10,
    ) -> list[DiscoveryResult]:
        """Search for potential lead sources."""
        raise NotImplementedError