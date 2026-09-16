import csv

from lead_collector.export.csv_exporter import CSVLeadExporter
from lead_collector.models import Lead, ValidationStatus


def create_lead() -> Lead:
    return Lead(
        company_name="Example Technologies",
        website="https://example.com",
        industry="Software",
        city="Ahmedabad",
        state="Gujarat",
        country="India",
        contact_name="John Doe",
        contact_role="Sales Manager",
        email="sales@example.com",
        phone="+91 98765 43210",
        linkedin_url=(
            "https://www.linkedin.com/company/example"
        ),
        source_url="https://example.com",
        lead_score=95,
        validation_status=ValidationStatus.VALID,
    )


def test_export_creates_csv_file(tmp_path):
    output_path = tmp_path / "exports" / "leads.csv"

    result = CSVLeadExporter().export(
        [create_lead()],
        output_path,
    )

    assert result == output_path
    assert output_path.exists()


def test_export_writes_header_and_lead(tmp_path):
    output_path = tmp_path / "leads.csv"

    CSVLeadExporter().export(
        [create_lead()],
        output_path,
    )

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1

    row = rows[0]

    assert row["company_name"] == "Example Technologies"
    assert row["industry"] == "Software"
    assert row["email"] == "sales@example.com"
    assert row["phone"] == "+91 98765 43210"
    assert row["lead_score"] == "95"
    assert row["validation_status"] == "valid"


def test_export_handles_optional_fields(tmp_path):
    output_path = tmp_path / "leads.csv"

    lead = Lead(
        company_name="Minimal Company",
        website="https://example.com",
    )

    CSVLeadExporter().export(
        [lead],
        output_path,
    )

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    row = rows[0]

    assert row["company_name"] == "Minimal Company"
    assert row["email"] == ""
    assert row["phone"] == ""
    assert row["linkedin_url"] == ""
    assert row["industry"] == ""


def test_export_handles_empty_lead_list(tmp_path):
    output_path = tmp_path / "leads.csv"

    CSVLeadExporter().export([], output_path)

    assert output_path.exists()

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert rows == []