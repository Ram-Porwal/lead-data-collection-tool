from lead_collector.models import Lead, ValidationStatus
from lead_collector.storage.database import LeadDatabase


def create_lead() -> Lead:
    return Lead(
        company_name="Example Technologies",
        website="https://example.com",
        email="sales@example.com",
        phone="+91 98765 43210",
        lead_score=80,
        validation_status=ValidationStatus.VALID,
    )


def test_initialize_creates_database(tmp_path):
    database_path = tmp_path / "test.db"

    database = LeadDatabase(database_path)
    database.initialize()

    assert database_path.exists()
    assert database.count() == 0


def test_insert_stores_lead(tmp_path):
    database_path = tmp_path / "test.db"

    database = LeadDatabase(database_path)
    database.initialize()

    lead = create_lead()
    database.insert(lead)

    assert database.count() == 1


def test_insert_multiple_leads(tmp_path):
    database_path = tmp_path / "test.db"

    database = LeadDatabase(database_path)
    database.initialize()

    database.insert(create_lead())
    database.insert(create_lead())

    assert database.count() == 2


def test_initialize_is_idempotent(tmp_path):
    database_path = tmp_path / "test.db"

    database = LeadDatabase(database_path)

    database.initialize()
    database.initialize()

    assert database.count() == 0