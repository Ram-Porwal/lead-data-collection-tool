from lead_collector.extraction.lead_extractor import LeadExtractor
from lead_collector.extraction.parser import ParsedPage
from lead_collector.models import ValidationStatus


def test_extract_creates_lead_from_parsed_page():
    page = ParsedPage(
        title="Example Technologies",
        description="A software company.",
        text=(
            "Contact us at sales@example.com. "
            "Call +91 98765 43210."
        ),
        links=[
            "https://example.com/about",
            "https://www.linkedin.com/company/example-technologies",
        ],
    )

    result = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert result.company_name == "Example Technologies"
    assert str(result.website) == "https://example.com/"
    assert str(result.email) == "sales@example.com"
    assert result.phone == "+91 98765 43210"
    assert (
        str(result.linkedin_url)
        == "https://www.linkedin.com/company/example-technologies"
    )
    assert str(result.source_url) == "https://example.com/"
    assert result.validation_status == ValidationStatus.PENDING


def test_extract_handles_missing_contact_information():
    page = ParsedPage(
        title="Example Company",
        description=None,
        text="We build software.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert result.company_name == "Example Company"
    assert result.email is None
    assert result.phone is None
    assert result.linkedin_url is None


def test_extract_uses_domain_when_title_is_missing():
    page = ParsedPage(
        title=None,
        description=None,
        text="Welcome to our website.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://www.acme-solutions.com",
    )

    assert result.company_name == "Acme Solutions"