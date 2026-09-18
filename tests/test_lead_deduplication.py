from lead_collector.models import Lead
from lead_collector.processing.lead_deduplication import deduplicate_leads


def make_lead(
    company_name: str,
    *,
    website: str | None = None,
    email: str | None = None,
) -> Lead:
    return Lead(
        company_name=company_name,
        website=website,
        email=email,
    )


def test_deduplicate_leads_removes_duplicate_websites():
    leads = [
        make_lead(
            "Company One",
            website="https://example.com",
        ),
        make_lead(
            "Company One Duplicate",
            website="https://example.com/",
        ),
        make_lead(
            "Company Two",
            website="https://other.com",
        ),
    ]

    unique_leads = deduplicate_leads(leads)

    assert len(unique_leads) == 2
    assert unique_leads[0].company_name == "Company One"
    assert unique_leads[1].company_name == "Company Two"


def test_deduplicate_leads_removes_duplicate_emails():
    leads = [
        make_lead(
            "Company One",
            email="sales@example.com",
        ),
        make_lead(
            "Company One Duplicate",
            email="SALES@example.com",
        ),
        make_lead(
            "Company Two",
            email="other@example.com",
        ),
    ]

    unique_leads = deduplicate_leads(leads)

    assert len(unique_leads) == 2
    assert unique_leads[0].company_name == "Company One"
    assert unique_leads[1].company_name == "Company Two"


def test_deduplicate_leads_keeps_leads_with_different_identity():
    leads = [
        make_lead(
            "Company One",
            website="https://one.com",
            email="one@example.com",
        ),
        make_lead(
            "Company Two",
            website="https://two.com",
            email="two@example.com",
        ),
    ]

    unique_leads = deduplicate_leads(leads)

    assert len(unique_leads) == 2


def test_deduplicate_leads_does_not_match_missing_websites():
    leads = [
        make_lead("Company One"),
        make_lead("Company Two"),
    ]

    unique_leads = deduplicate_leads(leads)

    assert len(unique_leads) == 2


def test_deduplicate_leads_does_not_match_missing_emails():
    leads = [
        make_lead(
            "Company One",
            website="https://one.com",
        ),
        make_lead(
            "Company Two",
            website="https://two.com",
        ),
    ]

    unique_leads = deduplicate_leads(leads)

    assert len(unique_leads) == 2


def test_deduplicate_leads_preserves_order():
    leads = [
        make_lead(
            "Third Company",
            website="https://third.com",
        ),
        make_lead(
            "First Company",
            website="https://first.com",
        ),
        make_lead(
            "Second Company",
            website="https://second.com",
        ),
    ]

    unique_leads = deduplicate_leads(leads)

    assert [lead.company_name for lead in unique_leads] == [
        "Third Company",
        "First Company",
        "Second Company",
    ]


def test_deduplicate_leads_handles_empty_input():
    assert deduplicate_leads([]) == []


def test_deduplicate_leads_removes_duplicate_when_either_identity_matches():
    leads = [
        make_lead(
            "Company One",
            website="https://example.com",
            email="one@example.com",
        ),
        make_lead(
            "Company One Duplicate",
            website="https://different.com",
            email="one@example.com",
        ),
    ]

    unique_leads = deduplicate_leads(leads)

    assert len(unique_leads) == 1
    assert unique_leads[0].company_name == "Company One"


def test_deduplicate_leads_does_not_treat_missing_identity_as_duplicate():
    leads = [
        make_lead(
            "Company One",
            website="https://example.com",
        ),
        make_lead(
            "Company Two",
            email="company2@example.com",
        ),
    ]

    unique_leads = deduplicate_leads(leads)

    assert len(unique_leads) == 2