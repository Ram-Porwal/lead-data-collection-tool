import pytest

from lead_collector.processing.normalization import (
    normalize_country,
    normalize_url,
)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://Example.COM/",
            "https://example.com/",
        ),
        (
            "https://example.com/about/",
            "https://example.com/about",
        ),
        (
            "https://example.com#about",
            "https://example.com/",
        ),
        (
            "https://example.com/about#team",
            "https://example.com/about",
        ),
        (
            "http://example.com:80/",
            "http://example.com/",
        ),
        (
            "https://example.com:443/",
            "https://example.com/",
        ),
        (
            "  https://example.com/about/  ",
            "https://example.com/about",
        ),
        (
            "",
            "",
        ),
    ],
)
def test_normalize_url(url, expected):
    assert normalize_url(url) == expected


from lead_collector.processing.normalization import normalize_country


def test_normalize_country_iso_alpha2():
    assert normalize_country("IN") == "India"
    assert normalize_country("US") == "United States"


def test_normalize_country_iso_alpha3():
    assert normalize_country("IND") == "India"
    assert normalize_country("GBR") == "United Kingdom"


def test_normalize_country_name_variants():
    assert normalize_country("india") == "India"
    assert normalize_country(" INDIA ") == "India"
    assert normalize_country("usa") == "United States"
    assert normalize_country("United Kingdom") == "United Kingdom"


def test_normalize_country_other_aliases():
    assert normalize_country("UAE") == "United Arab Emirates"
    assert normalize_country("AE") == "United Arab Emirates"


def test_normalize_country_preserves_unknown_values():
    assert normalize_country("Atlantis") == "Atlantis"


def test_normalize_country_handles_empty_values():
    assert normalize_country(None) is None
    assert normalize_country("") is None
    assert normalize_country("   ") is None