from lead_collector.models import Lead


class LeadScorer:
    """Calculate a data-completeness score for a lead."""

    def score(self, lead: Lead) -> int:
        """Return a lead quality score from 0 to 100."""

        return self.breakdown(lead)["total"]

    def breakdown(self, lead: Lead) -> dict[str, int]:
        """Return the score contribution of each lead data category."""

        breakdown = {
            "company_name": 20 if lead.company_name else 0,
            "website": 20 if lead.website else 0,
            "email": 25 if lead.email else 0,
            "phone": 15 if lead.phone else 0,
            "linkedin_url": 10 if lead.linkedin_url else 0,
            "industry": 5 if lead.industry else 0,
            "location": (
                5
                if lead.city or lead.state or lead.country
                else 0
            ),
        }

        breakdown["total"] = sum(breakdown.values())

        return breakdown