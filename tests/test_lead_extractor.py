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


def test_extract_cleans_seo_company_title():
    page = ParsedPage(
        title="Software Development Company Since 1987 | SPEC India",
        description="Software development company.",
        text="Contact us.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://www.spec-india.com",
    )

    assert result.company_name == "SPEC India"


def test_extract_uses_text_after_last_pipe():
    page = ParsedPage(
        title="Best Software Solutions | Technology | Acme Technologies",
        description=None,
        text="We build software.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://acme-technologies.com",
    )

    assert result.company_name == "Acme Technologies"


def test_extract_ignores_empty_text_after_pipe():
    page = ParsedPage(
        title="Acme Technologies | ",
        description=None,
        text="We build software.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://acme-technologies.com",
    )

    assert result.company_name == "Acme Technologies"


def test_extract_ignores_generic_website_title_suffix():
    page = ParsedPage(
        title="Acme Technologies | Official Website",
        description=None,
        text="We build software.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://acme-technologies.com",
    )

    assert result.company_name == "Acme Technologies"


def test_extract_prefers_company_name_from_talentica_style_title():
    page = ParsedPage(
        title=(
            "Software Product Development Company & "
            "Engineering Experts"
        ),
        description="Software product development company.",
        text="We build software products and engineering solutions.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://www.talentica.com",
    )

    assert result.company_name == "Talentica"


def test_extract_prefers_json_ld_organization_name():
    page = ParsedPage(
        title="Software Product Development Company & Engineering Experts",
        description="Software product development company.",
        site_name="Talentica",
        canonical_url="https://www.talentica.com/",
        organization_name="Talentica",
        text="Software engineering company.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://www.talentica.com",
    )

    assert result.company_name == "Talentica"


def test_extract_prefers_site_name_over_generic_title():
    page = ParsedPage(
        title="Enterprise Software Development & Technology Solutions",
        description="Technology company.",
        site_name="Example Technologies",
        canonical_url="https://example.com/",
        organization_name=None,
        text="We build enterprise software.",
        links=[],
    )

    result = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert result.company_name == "Example Technologies"


def test_extract_uses_organization_metadata():
    page = ParsedPage(
        title="Example Company",
        description=None,
        text="Example Company",
        links=[],
        organization_name="Example Technologies",
        organization_industry="Software",
        organization_email="structured@example.com",
        organization_telephone="+91 98765 43210",
        organization_city="Ahmedabad",
        organization_state="Gujarat",
        organization_country="India",
    )

    lead = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert lead.company_name == "Example Technologies"
    assert lead.industry == "Software"
    assert lead.email == "structured@example.com"
    assert lead.phone == "+91 98765 43210"
    assert lead.city == "Ahmedabad"
    assert lead.state == "Gujarat"
    assert lead.country == "India"


def test_extract_falls_back_to_page_text_when_structured_contact_data_missing():
    page = ParsedPage(
        title="Example Company",
        description=None,
        text=(
            "Contact us at fallback@example.com "
            "or call +91 98765 43210"
        ),
        links=[],
    )

    lead = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert lead.email == "fallback@example.com"
    assert lead.phone == "+91 98765 43210"


def test_extract_rejects_invalid_structured_phone():
    page = ParsedPage(
        title="Example Company",
        description=None,
        text="Contact sales@example.com",
        links=[],
        organization_name="Example Technologies",
        organization_telephone="+91 123",
    )

    lead = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert lead.phone is None


def test_extract_normalizes_structured_phone():
    page = ParsedPage(
        title="Example Company",
        description=None,
        text="Example Company",
        links=[],
        organization_name="Example Technologies",
        organization_telephone="+1 (212) 867-5309",
    )

    lead = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert lead.phone == "+1 212-867-5309"


def test_extract_normalizes_structured_country():
    page = ParsedPage(
        title="Example Company",
        description=None,
        text="Example Company",
        links=[],
        organization_name="Example Technologies",
        organization_country="IN",
    )

    lead = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert lead.country == "India"


def test_extract_sets_phone_country():
    page = ParsedPage(
        title="Example Company",
        description=None,
        text="Example Company",
        links=[],
        organization_name="Example Technologies",
        organization_telephone="+1 (212) 867-5309",
    )

    lead = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert lead.phone == "+1 212-867-5309"
    assert lead.phone_country == "US"


def test_extract_sets_indian_phone_country():
    page = ParsedPage(
        title="Example Company",
        description=None,
        text="Example Company",
        links=[],
        organization_name="Example Technologies",
        organization_telephone="+91 98765 43210",
    )

    lead = LeadExtractor().extract(
        page,
        "https://example.com",
    )

    assert lead.phone == "+91 98765 43210"
    assert lead.phone_country == "IN"