from lead_collector.models import Lead, ValidationStatus
from lead_collector.pipeline import PipelineResult
from lead_collector.reporting.summary import PipelineSummary


def make_lead(
    *,
    company_name: str = "Example Company",
    validation_status: ValidationStatus = ValidationStatus.VALID,
) -> Lead:
    return Lead(
        company_name=company_name,
        website="https://example.com",
        email="hello@example.com",
        validation_status=validation_status,
    )


def make_result(
    *,
    discovered: int = 10,
    rejected_by_quality: int = 2,
    unique_results: int = 8,
    fetched: int = 7,
    failed_fetches: int = 1,
    challenge_pages: int = 0,
    lead_duplicates: int = 1,
    leads: list[Lead] | None = None,
    valid_leads: int = 5,
    invalid_leads: int = 1,
) -> PipelineResult:
    if leads is None:
        leads = [
            make_lead(company_name=f"Company {index}")
            for index in range(valid_leads)
        ] + [
            make_lead(
                company_name="Invalid Company",
                validation_status=ValidationStatus.INVALID,
            )
            for _ in range(invalid_leads)
        ]

    return PipelineResult(
        discovered=discovered,
        rejected_by_quality=rejected_by_quality,
        unique_results=unique_results,
        fetched=fetched,
        failed_fetches=failed_fetches,
        challenge_pages=challenge_pages,
        lead_duplicates=lead_duplicates,
        valid_leads=valid_leads,
        invalid_leads=invalid_leads,
        leads=leads,
    )


def test_summary_from_result_copies_pipeline_metrics():
    result = make_result()

    summary = PipelineSummary.from_result(result)

    assert summary.discovered == 10
    assert summary.rejected_by_quality == 2
    assert summary.unique_results == 8
    assert summary.fetched == 7
    assert summary.failed_fetches == 1
    assert summary.challenge_pages == 0
    assert summary.lead_duplicates == 1
    assert summary.final_leads == 6
    assert summary.valid_leads == 5
    assert summary.invalid_leads == 1


def test_summary_counts_final_leads_from_result():
    leads = [
        make_lead(company_name="Company A"),
        make_lead(company_name="Company B"),
        make_lead(
            company_name="Company C",
            validation_status=ValidationStatus.INVALID,
        ),
    ]

    result = make_result(
        leads=leads,
        valid_leads=2,
        invalid_leads=1,
    )

    summary = PipelineSummary.from_result(result)

    assert summary.final_leads == 3


def test_summary_supports_empty_pipeline_result():
    result = make_result(
        discovered=0,
        rejected_by_quality=0,
        unique_results=0,
        fetched=0,
        failed_fetches=0,
        challenge_pages=0,
        lead_duplicates=0,
        leads=[],
        valid_leads=0,
        invalid_leads=0,
    )

    summary = PipelineSummary.from_result(result)

    assert summary.discovered == 0
    assert summary.rejected_by_quality == 0
    assert summary.unique_results == 0
    assert summary.fetched == 0
    assert summary.failed_fetches == 0
    assert summary.challenge_pages == 0
    assert summary.lead_duplicates == 0
    assert summary.final_leads == 0
    assert summary.valid_leads == 0
    assert summary.invalid_leads == 0


def test_summary_is_immutable():
    result = make_result()

    summary = PipelineSummary.from_result(result)

    try:
        summary.discovered = 100
    except AttributeError:
        pass
    else:
        raise AssertionError("PipelineSummary should be immutable")