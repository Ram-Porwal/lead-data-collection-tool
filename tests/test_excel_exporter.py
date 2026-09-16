from openpyxl import load_workbook

from lead_collector.export.excel_exporter import ExcelLeadExporter
from lead_collector.models import Lead, ValidationStatus


def create_lead() -> Lead:
    return Lead(
        company_name="Example Technologies",
        website="https://example.com",
        industry="Software",
        city="Ahmedabad",
        state="Gujarat",
        country="India",
        email="sales@example.com",
        phone="+91 98765 43210",
        linkedin_url=(
            "https://www.linkedin.com/company/example"
        ),
        lead_score=95,
        validation_status=ValidationStatus.VALID,
    )


def test_export_creates_excel_file(tmp_path):
    output_path = tmp_path / "exports" / "leads.xlsx"

    result = ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    assert result == output_path
    assert output_path.exists()


def test_export_writes_lead_data(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet["B2"].value == "Example Technologies"
    assert worksheet["D2"].value == "Software"
    assert worksheet["J2"].value == "sales@example.com"
    assert worksheet["K2"].value == "+91 98765 43210"
    assert worksheet["N2"].value == 95
    assert worksheet["O2"].value == "valid"


def test_export_formats_header(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet["A1"].value == "id"
    assert worksheet["B1"].value == "company_name"
    assert worksheet["A1"].font.bold is True


def test_export_freezes_header_and_enables_filter(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet.freeze_panes == "A2"
    assert worksheet.auto_filter.ref == worksheet.dimensions


def test_export_handles_empty_leads(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export([], output_path)

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet.max_row == 1
    assert worksheet["A1"].value == "id"