from lead_collector.models import Lead, ValidationStatus
from lead_collector.storage.database import LeadDatabase
from lead_collector.storage.repository import LeadRepository


def create_lead(
    company_name: str,
    score: int,
    status: ValidationStatus,
) -> Lead:
    return Lead(
        company_name=company_name,
        website="https://example.com",
        email=f"{company_name.lower().replace(' ', '')}@example.com",
        lead_score=score,
        validation_status=status,
    )


def setup_database(tmp_path):
    database_path = tmp_path / "test.db"

    database = LeadDatabase(database_path)
    database.initialize()

    return database_path, database


def test_get_by_id_returns_lead(tmp_path):
    database_path, database = setup_database(tmp_path)

    lead = create_lead(
        "Example Technologies",
        80,
        ValidationStatus.VALID,
    )

    database.insert(lead)

    repository = LeadRepository(str(database_path))

    result = repository.get_by_id(lead.id)

    assert result is not None
    assert result.id == lead.id
    assert result.company_name == "Example Technologies"
    assert result.lead_score == 80
    assert result.validation_status == ValidationStatus.VALID


def test_get_by_id_returns_none_for_missing_lead(tmp_path):
    database_path, _ = setup_database(tmp_path)

    repository = LeadRepository(str(database_path))

    result = repository.get_by_id(
        create_lead(
            "Missing",
            40,
            ValidationStatus.INVALID,
        ).id
    )

    assert result is None


def test_get_all_returns_all_leads(tmp_path):
    database_path, database = setup_database(tmp_path)

    first = create_lead(
        "First Company",
        60,
        ValidationStatus.VALID,
    )
    second = create_lead(
        "Second Company",
        40,
        ValidationStatus.INVALID,
    )

    database.insert(first)
    database.insert(second)

    repository = LeadRepository(str(database_path))

    results = repository.get_all()

    assert len(results) == 2
    assert results[0].company_name == "First Company"
    assert results[1].company_name == "Second Company"


def test_get_valid_leads_returns_only_valid_leads_sorted_by_score(
    tmp_path,
):
    database_path, database = setup_database(tmp_path)

    low_score = create_lead(
        "Low Score",
        60,
        ValidationStatus.VALID,
    )
    high_score = create_lead(
        "High Score",
        90,
        ValidationStatus.VALID,
    )
    invalid = create_lead(
        "Invalid Company",
        100,
        ValidationStatus.INVALID,
    )

    database.insert(low_score)
    database.insert(high_score)
    database.insert(invalid)

    repository = LeadRepository(str(database_path))

    results = repository.get_valid_leads()

    assert len(results) == 2
    assert results[0].company_name == "High Score"
    assert results[1].company_name == "Low Score"