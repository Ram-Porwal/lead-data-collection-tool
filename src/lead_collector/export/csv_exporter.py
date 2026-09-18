import csv
from pathlib import Path

from lead_collector.models import Lead


class CSVLeadExporter:
    """Export leads to CSV format."""

    FIELDNAMES = [
        "id",
        "company_name",
        "website",
        "industry",
        "city",
        "state",
        "country",
        "contact_name",
        "contact_role",
        "email",
        "phone",
        "phone_country",
        "linkedin_url",
        "source_url",
        "lead_score",
        "validation_status",
        "created_at",
    ]

    def export(
        self,
        leads: list[Lead],
        output_path: str | Path,
    ) -> Path:
        """Export leads to a CSV file."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDNAMES,
            )

            writer.writeheader()

            for lead in leads:
                writer.writerow(
                    {
                        "id": str(lead.id),
                        "company_name": lead.company_name,
                        "website": (
                            str(lead.website)
                            if lead.website
                            else ""
                        ),
                        "industry": lead.industry or "",
                        "city": lead.city or "",
                        "state": lead.state or "",
                        "country": lead.country or "",
                        "contact_name": lead.contact_name or "",
                        "contact_role": lead.contact_role or "",
                        "email": (
                            str(lead.email)
                            if lead.email
                            else ""
                        ),
                        "phone": lead.phone or "",
                        "phone_country": lead.phone_country or "",
                        "linkedin_url": (
                            str(lead.linkedin_url)
                            if lead.linkedin_url
                            else ""
                        ),
                        "source_url": (
                            str(lead.source_url)
                            if lead.source_url
                            else ""
                        ),
                        "lead_score": lead.lead_score,
                        "validation_status": (
                            lead.validation_status.value
                        ),
                        "created_at": lead.created_at.isoformat(),
                    }
                )

        return path