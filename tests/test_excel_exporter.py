from openpyxl import load_workbook

from lead_collector.export.excel_exporter import ExcelLeadExporter
from lead_collector.models import Lead, ValidationStatus
from lead_collector.reporting.summary import PipelineSummary


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
        phone_country="IN",
        linkedin_url=(
            "https://www.linkedin.com/company/example"
        ),
        source_url="https://example.com",
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

    assert worksheet["A2"].value == "Example Technologies"
    assert worksheet["C2"].value == "Software"
    assert worksheet["I2"].value == "sales@example.com"
    assert worksheet["J2"].value == "+91 98765 43210"
    assert worksheet["K2"].value == "IN"
    assert worksheet["N2"].value == "valid"
    assert worksheet["M2"].value == 95
    assert worksheet["N2"].value is not None


def test_export_formats_headers(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet["A1"].value == "Company Name"
    assert worksheet["B1"].value == "Website"
    assert worksheet["I1"].value == "Email"
    assert worksheet["M1"].value == "Lead Score"
    assert worksheet["K1"].value == "Phone Country"
    assert worksheet["P1"].value == "Created At"
    assert worksheet["Q1"].value == "ID"
    assert worksheet["A1"].font.bold is True
    assert worksheet["A1"].font.color.rgb == "00FFFFFF"


def test_export_freezes_header(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet.freeze_panes == "A2"


def test_export_creates_excel_table(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert "LeadReport" in worksheet.tables
    assert worksheet.tables["LeadReport"].ref == "A1:Q2"


def test_export_creates_hyperlinks(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet["B2"].value == "Open Website"
    assert worksheet["B2"].hyperlink.target == "https://example.com/"

    assert worksheet["L2"].value == "LinkedIn"
    assert (
        worksheet["L2"].hyperlink.target
        == "https://www.linkedin.com/company/example"
    )

    assert worksheet["O2"].value == "View Source"
    assert worksheet["O2"].hyperlink.target == "https://example.com/"


def test_export_formats_created_at(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(
        [create_lead()],
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet["P2"].number_format == "yyyy-mm-dd hh:mm"


def test_export_handles_empty_leads(tmp_path):
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export([], output_path)

    workbook = load_workbook(output_path)
    worksheet = workbook["Leads"]

    assert worksheet.max_row == 1
    assert worksheet["A1"].value == "Company Name"
    assert worksheet["Q1"].value == "ID"


def make_pipeline_summary() -> PipelineSummary:
    return PipelineSummary(
        discovered=10,
        rejected_by_quality=2,
        unique_results=8,
        fetched=7,
        failed_fetches=1,
        challenge_pages=1,
        lead_duplicates=1,
        final_leads=6,
        valid_leads=5,
        invalid_leads=1,
    )


def test_export_creates_summary_sheet(tmp_path):
    leads = [create_lead()]
    output_path = tmp_path / "leads.xlsx"
    summary = make_pipeline_summary()

    ExcelLeadExporter().export(
        leads,
        output_path,
        summary=summary,
    )

    workbook = load_workbook(output_path)

    assert workbook.sheetnames == ["Summary", "Leads"]


def test_summary_sheet_contains_pipeline_metrics(tmp_path):
    leads = [create_lead()]
    output_path = tmp_path / "leads.xlsx"
    summary = make_pipeline_summary()

    ExcelLeadExporter().export(
        leads,
        output_path,
        summary=summary,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook["Summary"]

    assert worksheet["A1"].value == "Lead Collection Summary"
    assert worksheet["A3"].value == "Discovered Results"
    assert worksheet["B3"].value == 10
    assert worksheet["A4"].value == "Rejected by Quality"
    assert worksheet["B4"].value == 2
    assert worksheet["A5"].value == "Unique Accepted Results"
    assert worksheet["B5"].value == 8
    assert worksheet["A6"].value == "Websites Fetched"
    assert worksheet["B6"].value == 7
    assert worksheet["A7"].value == "Failed Fetches"
    assert worksheet["B7"].value == 1
    assert worksheet["A8"].value == "Challenge Pages"
    assert worksheet["B8"].value == 1
    assert worksheet["A9"].value == "Lead Duplicates"
    assert worksheet["B9"].value == 1
    assert worksheet["A10"].value == "Final Leads"
    assert worksheet["B10"].value == 6
    assert worksheet["A11"].value == "Valid Leads"
    assert worksheet["B11"].value == 5
    assert worksheet["A12"].value == "Invalid Leads"
    assert worksheet["B12"].value == 1


def test_summary_sheet_is_first_worksheet(tmp_path):
    leads = [create_lead()]
    output_path = tmp_path / "leads.xlsx"
    summary = make_pipeline_summary()

    ExcelLeadExporter().export(
        leads,
        output_path,
        summary=summary,
    )

    workbook = load_workbook(output_path)

    assert workbook.sheetnames[0] == "Summary"
    assert workbook.sheetnames[1] == "Leads"


def test_export_without_summary_preserves_existing_api(tmp_path):
    leads = [create_lead()]
    output_path = tmp_path / "leads.xlsx"

    ExcelLeadExporter().export(leads, output_path)

    workbook = load_workbook(output_path)

    assert workbook.sheetnames == ["Leads"]