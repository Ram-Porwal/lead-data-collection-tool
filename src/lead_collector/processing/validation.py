from lead_collector.models import Lead, ValidationStatus
from lead_collector.processing.scoring import LeadScorer


class LeadValidator:
    """Validate lead data and assign a validation status and score."""

    def __init__(self, scorer: LeadScorer | None = None) -> None:
        self._scorer = scorer or LeadScorer()

    def validate(self, lead: Lead) -> Lead:
        """Validate a lead and update its status and score."""

        lead.lead_score = self._scorer.score(lead)

        if not lead.company_name.strip():
            lead.validation_status = ValidationStatus.INVALID
            return lead

        if not lead.website:
            lead.validation_status = ValidationStatus.INVALID
            return lead

        if not lead.email and not lead.phone:
            lead.validation_status = ValidationStatus.INVALID
            return lead

        lead.validation_status = ValidationStatus.VALID
        return lead