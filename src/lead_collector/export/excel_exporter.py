from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from lead_collector.models import Lead


class ExcelLeadExporter:
    """Export leads to a formatted Excel workbook."""

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
        """Export leads to an Excel workbook."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Leads"

        worksheet.append(self.FIELDNAMES)

        for cell in worksheet[1]:
            cell.font = Font(bold=True)

        for lead in leads:
            worksheet.append(
                [
                    str(lead.id),
                    lead.company_name,
                    str(lead.website) if lead.website else "",
                    lead.industry or "",
                    lead.city or "",
                    lead.state or "",
                    lead.country or "",
                    lead.contact_name or "",
                    lead.contact_role or "",
                    str(lead.email) if lead.email else "",
                    lead.phone or "",
                    (
                        str(lead.linkedin_url)
                        if lead.linkedin_url
                        else ""
                    ),
                    (
                        str(lead.source_url)
                        if lead.source_url
                        else ""
                    ),
                    lead.lead_score,
                    lead.validation_status.value,
                    lead.created_at.isoformat(),
                ]
            )

        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        for column_cells in worksheet.columns:
            max_length = max(
                len(str(cell.value or ""))
                for cell in column_cells
            )

            column_letter = get_column_letter(
                column_cells[0].column
            )

            worksheet.column_dimensions[
                column_letter
            ].width = min(max_length + 2, 40)

        workbook.save(path)

        return path