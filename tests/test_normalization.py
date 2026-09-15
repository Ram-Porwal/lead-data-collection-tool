import pytest

from lead_collector.processing.normalization import normalize_url


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