from datetime import datetime, timezone

from lead_collector.models import Lead, ValidationStatus
from lead_collector.storage.database import LeadDatabase


def create_lead(
    website: str,
    *,
    email: str | None = None,
    phone: str | None = None,
    company_name: str = "Test Company",
) -> Lead:
    return Lead(
        company_name=company_name,
        website=website,
        email=email,
        phone=phone,
        validation_status=ValidationStatus.VALID,
        created_at=datetime.now(timezone.utc),
    )


def test_database_upserts_duplicate_website(tmp_path):
    database = LeadDatabase(tmp_path / "leads.db")
    database.initialize()

    first = create_lead(
        "https://example.com/",
        company_name="Example Company",
    )

    second = create_lead(
        "https://example.com",
        company_name="Example Company Updated",
    )

    database.insert(first)
    database.insert(second)

    assert database.count() == 1


def test_database_upsert_preserves_existing_contact_data(tmp_path):
    database = LeadDatabase(tmp_path / "leads.db")
    database.initialize()

    first = create_lead(
        "https://example.com",
        email="hello@example.com",
        phone="+1 212-555-0100",
    )

    second = create_lead(
        "https://example.com/",
        email=None,
        phone=None,
    )

    database.insert(first)
    database.insert(second)

    from lead_collector.storage.repository import LeadRepository

    repository = LeadRepository(tmp_path / "leads.db")
    leads = repository.get_all()

    assert len(leads) == 1
    assert str(leads[0].email) == "hello@example.com"
    assert leads[0].phone == "+1 212-555-0100"


def test_database_allows_different_websites(tmp_path):
    database = LeadDatabase(tmp_path / "leads.db")
    database.initialize()

    database.insert(
        create_lead("https://example-one.com")
    )

    database.insert(
        create_lead("https://example-two.com")
    )

    assert database.count() == 2