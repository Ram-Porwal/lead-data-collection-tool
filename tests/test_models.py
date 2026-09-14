import pytest
from pydantic import ValidationError

from lead_collector.models import Lead, ValidationStatus


def test_valid_lead():
    lead = Lead(
        company_name="ABC Technologies",
        website="https://example.com",
        industry="Software",
        city="Ahmedabad",
        state="Gujarat",
        country="India",
        email="hello@example.com",
        lead_score=80,
    )

    assert lead.company_name == "ABC Technologies"
    assert lead.email == "hello@example.com"
    assert lead.lead_score == 80
    assert lead.validation_status == ValidationStatus.PENDING


def test_company_name_cannot_be_empty():
    with pytest.raises(ValidationError):
        Lead(company_name="")


def test_email_must_be_valid():
    with pytest.raises(ValidationError):
        Lead(
            company_name="ABC Technologies",
            email="not-an-email",
        )


def test_lead_score_must_be_between_zero_and_hundred():
    with pytest.raises(ValidationError):
        Lead(
            company_name="ABC Technologies",
            lead_score=150,
        )


def test_lead_score_cannot_be_negative():
    with pytest.raises(ValidationError):
        Lead(
            company_name="ABC Technologies",
            lead_score=-10,
        )


def test_optional_fields_can_be_missing():
    lead = Lead(company_name="ABC Technologies")

    assert lead.website is None
    assert lead.email is None
    assert lead.phone is None
    assert lead.linkedin_url is None


def test_id_is_generated_automatically():
    lead = Lead(company_name="ABC Technologies")

    assert lead.id is not None


def test_validation_status_defaults_to_pending():
    lead = Lead(company_name="ABC Technologies")

    assert lead.validation_status == ValidationStatus.PENDING