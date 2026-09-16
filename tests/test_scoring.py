from lead_collector.models import Lead
from lead_collector.processing.scoring import LeadScorer


def test_score_complete_lead():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        email="sales@example.com",
        phone="+91 98765 43210",
        linkedin_url="https://www.linkedin.com/company/example",
        industry="Software",
        city="Ahmedabad",
    )

    assert LeadScorer().score(lead) == 100


def test_score_company_and_website_only():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
    )

    assert LeadScorer().score(lead) == 40


def test_score_email_and_phone():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        email="sales@example.com",
        phone="+91 98765 43210",
    )

    assert LeadScorer().score(lead) == 80


def test_score_location_counts_as_one_category():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        city="Ahmedabad",
        state="Gujarat",
        country="India",
    )

    assert LeadScorer().score(lead) == 45


def test_score_minimum_lead():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
    )

    assert LeadScorer().score(lead) == 40