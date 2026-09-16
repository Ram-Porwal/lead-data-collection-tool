from lead_collector.models import Lead


class LeadScorer:
    """Calculate a data-completeness score for a lead."""

    def score(self, lead: Lead) -> int:
        """Return a lead quality score from 0 to 100."""

        score = 0

        if lead.company_name:
            score += 20

        if lead.website:
            score += 20

        if lead.email:
            score += 25

        if lead.phone:
            score += 15

        if lead.linkedin_url:
            score += 10

        if lead.industry:
            score += 5

        if lead.city or lead.state or lead.country:
            score += 5

        return score