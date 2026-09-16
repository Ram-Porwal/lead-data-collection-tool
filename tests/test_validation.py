from lead_collector.models import Lead, ValidationStatus
from lead_collector.processing.validation import LeadValidator


def test_validate_accepts_complete_lead():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        email="sales@example.com",
        phone="+91 98765 43210",
    )

    result = LeadValidator().validate(lead)

    assert result.validation_status == ValidationStatus.VALID


def test_validate_accepts_lead_with_phone_only():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        phone="+91 98765 43210",
    )

    result = LeadValidator().validate(lead)

    assert result.validation_status == ValidationStatus.VALID


def test_validate_accepts_lead_with_email_only():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        email="sales@example.com",
    )

    result = LeadValidator().validate(lead)

    assert result.validation_status == ValidationStatus.VALID


def test_validate_rejects_missing_website():
    lead = Lead(
        company_name="Example Technologies",
        email="sales@example.com",
    )

    result = LeadValidator().validate(lead)

    assert result.validation_status == ValidationStatus.INVALID


def test_validate_rejects_missing_contact_information():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
    )

    result = LeadValidator().validate(lead)

    assert result.validation_status == ValidationStatus.INVALID


def test_validate_assigns_lead_score():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        email="sales@example.com",
        phone="+91 98765 43210",
    )

    result = LeadValidator().validate(lead)

    assert result.lead_score == 80


def test_validate_assigns_score_to_invalid_lead():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
    )

    result = LeadValidator().validate(lead)

    assert result.lead_score == 40
    assert result.validation_status == ValidationStatus.INVALID