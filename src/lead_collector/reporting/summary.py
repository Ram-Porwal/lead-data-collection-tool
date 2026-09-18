from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lead_collector.pipeline import PipelineResult


@dataclass(frozen=True)
class PipelineSummary:
    """Client-facing summary of a lead collection pipeline run."""

    discovered: int
    rejected_by_quality: int
    unique_results: int
    fetched: int
    failed_fetches: int
    challenge_pages: int
    lead_duplicates: int
    final_leads: int
    valid_leads: int
    invalid_leads: int

    @classmethod
    def from_result(cls, result: PipelineResult) -> "PipelineSummary":
        """Create a summary from a completed pipeline result."""
        return cls(
            discovered=result.discovered,
            rejected_by_quality=result.rejected_by_quality,
            unique_results=result.unique_results,
            fetched=result.fetched,
            failed_fetches=result.failed_fetches,
            challenge_pages=result.challenge_pages,
            lead_duplicates=result.lead_duplicates,
            final_leads=len(result.leads),
            valid_leads=result.valid_leads,
            invalid_leads=result.invalid_leads,
        )