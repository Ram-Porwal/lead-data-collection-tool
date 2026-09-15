from lead_collector.discovery.models import DiscoveryResult
from lead_collector.processing.deduplication import deduplicate_results


def make_result(url: str, position: int) -> DiscoveryResult:
    return DiscoveryResult(
        title=f"Company {position}",
        url=url,
        source="test",
        position=position,
    )


def test_deduplicate_results_removes_duplicate_urls():
    results = [
        make_result("https://example.com", 1),
        make_result("https://example.com/", 2),
        make_result("https://other.com", 3),
    ]

    unique_results = deduplicate_results(results)

    assert len(unique_results) == 2
    assert unique_results[0].title == "Company 1"
    assert unique_results[1].title == "Company 3"


def test_deduplicate_results_preserves_order():
    results = [
        make_result("https://third.com", 1),
        make_result("https://first.com", 2),
        make_result("https://second.com", 3),
    ]

    unique_results = deduplicate_results(results)

    assert [result.title for result in unique_results] == [
        "Company 1",
        "Company 2",
        "Company 3",
    ]


def test_deduplicate_results_keeps_distinct_paths():
    results = [
        make_result("https://example.com/about", 1),
        make_result("https://example.com/contact", 2),
    ]

    unique_results = deduplicate_results(results)

    assert len(unique_results) == 2


def test_deduplicate_results_handles_empty_input():
    assert deduplicate_results([]) == []