from lead_collector.models import Lead
from lead_collector.processing.scoring import LeadScorer


def test_breakdown_for_complete_lead():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        email="sales@example.com",
        phone="+91 98765 43210",
        linkedin_url="https://www.linkedin.com/company/example",
        industry="Software",
        city="Ahmedabad",
    )

    breakdown = LeadScorer().breakdown(lead)

    assert breakdown == {
        "company_name": 20,
        "website": 20,
        "email": 25,
        "phone": 15,
        "linkedin_url": 10,
        "industry": 5,
        "location": 5,
        "total": 100,
    }


def test_breakdown_for_company_and_website_only():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
    )

    breakdown = LeadScorer().breakdown(lead)

    assert breakdown == {
        "company_name": 20,
        "website": 20,
        "email": 0,
        "phone": 0,
        "linkedin_url": 0,
        "industry": 0,
        "location": 0,
        "total": 40,
    }


def test_breakdown_location_counts_as_one_category():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        city="Ahmedabad",
        state="Gujarat",
        country="India",
    )

    breakdown = LeadScorer().breakdown(lead)

    assert breakdown["location"] == 5
    assert breakdown["total"] == 45


def test_breakdown_total_matches_score():
    lead = Lead(
        company_name="Example Technologies",
        website="https://example.com",
        email="sales@example.com",
        industry="Software",
    )

    scorer = LeadScorer()

    breakdown = scorer.breakdown(lead)

    assert breakdown["total"] == scorer.score(lead)