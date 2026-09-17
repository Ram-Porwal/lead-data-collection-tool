from lead_collector.discovery.models import DiscoveryResult
from lead_collector.discovery.quality import DiscoveryQualityFilter


def make_result(url: str) -> DiscoveryResult:
    return DiscoveryResult(
        title="Example Result",
        url=url,
        snippet="Example snippet",
        source="test",
    )


def test_accepts_company_website() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result("https://example.com")
    )

    assert result.accepted is True
    assert result.reason == "accepted"


def test_rejects_wikipedia() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result(
            "https://en.wikipedia.org/wiki/List_of_Indian_IT_companies"
        )
    )

    assert result.accepted is False
    assert result.reason == "blocked domain"


def test_rejects_article_page() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result(
            "https://example.com/articles/software-companies"
        )
    )

    assert result.accepted is False
    assert result.reason == "non-business page"


def test_rejects_screener_market_page() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result(
            "https://www.screener.in/market/IN08/IN0801/"
        )
    )

    assert result.accepted is False
    assert result.reason == "blocked domain"


def test_rejects_linkedin_share_url() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result(
            "https://www.linkedin.com/shareArticle?url=https://example.com"
        )
    )

    assert result.accepted is False
    assert result.reason == "blocked domain"


def test_rejects_linkedin_showcase_url() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result(
            "https://www.linkedin.com/showcase/example/"
        )
    )

    assert result.accepted is False
    assert result.reason == "blocked domain"


def test_filter_removes_low_quality_results() -> None:
    quality_filter = DiscoveryQualityFilter()

    results = [
        make_result("https://company-one.com"),
        make_result("https://en.wikipedia.org/wiki/Example"),
        make_result("https://company-two.com"),
    ]

    filtered = quality_filter.filter(results)

    assert len(filtered) == 2
    assert str(filtered[0].url) == "https://company-one.com/"
    assert str(filtered[1].url) == "https://company-two.com/"


def test_rejects_youtube() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result("https://www.youtube.com/watch?v=example")
    )

    assert result.accepted is False
    assert result.reason == "blocked domain"


def test_rejects_scribd() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result("https://www.scribd.com/document/example")
    )

    assert result.accepted is False
    assert result.reason == "blocked domain"


def test_rejects_naukri() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result("https://www.naukri.com/it-companies-in-india")
    )

    assert result.accepted is False
    assert result.reason == "blocked domain"


def test_rejects_moneycontrol() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = quality_filter.check(
        make_result(
            "https://www.moneycontrol.com/stocks/marketinfo/example"
        )
    )

    assert result.accepted is False
    assert result.reason == "blocked domain"


def test_rejects_list_title() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = DiscoveryResult(
        title="Top 50 Software Companies in India",
        url="https://example.com/company-page",
        snippet="Example",
        source="test",
    )

    checked = quality_filter.check(result)

    assert checked.accepted is False
    assert checked.reason == "list or article result"


def test_accepts_company_with_normal_title() -> None:
    quality_filter = DiscoveryQualityFilter()

    result = DiscoveryResult(
        title="ABC Technologies",
        url="https://abc-technologies.com",
        snippet="Software company",
        source="test",
    )

    checked = quality_filter.check(result)

    assert checked.accepted is True
    assert checked.reason == "accepted"