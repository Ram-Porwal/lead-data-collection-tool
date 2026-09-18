from lead_collector.extraction.fields import (
    extract_emails,
    extract_linkedin_url,
    extract_phone_numbers,
)


def test_extract_emails():
    text = """
    Contact us at Sales@Example.com or support@example.com.
    You can also email Sales@Example.com.
    """

    result = extract_emails(text)

    assert result == [
        "sales@example.com",
        "support@example.com",
    ]


def test_extract_emails_returns_empty_for_no_matches():
    assert extract_emails("No contact information here.") == []


def test_extract_phone_numbers():
    text = """
    Call us at +91 98765 43210 or +1 (212) 867-5309.
    """

    result = extract_phone_numbers(text)

    assert result == [
        "+91 98765 43210",
        "+1 212-867-5309",
    ]


def test_extract_phone_numbers_returns_empty_for_no_matches():
    assert extract_phone_numbers("No phone number here.") == []


def test_extract_linkedin_url():
    urls = [
        "https://example.com/about",
        "https://www.linkedin.com/company/example",
        "https://example.com/contact",
    ]

    assert (
        extract_linkedin_url(urls)
        == "https://www.linkedin.com/company/example"
    )


def test_extract_linkedin_url_returns_none_when_missing():
    urls = [
        "https://example.com/about",
        "https://github.com/example",
    ]

    assert extract_linkedin_url(urls) is None


def test_extract_phone_numbers_ignores_decimal_numbers():
    text = """
    Ratings: 4.7 4.7 4.8
    """

    assert extract_phone_numbers(text) == []


def test_extract_phone_numbers_ignores_year_like_values():
    text = """
    Updated in 2026 - 13.
    """

    assert extract_phone_numbers(text) == []


def test_normalize_phone_number():
    from lead_collector.extraction.fields import normalize_phone_number

    assert (
        normalize_phone_number("+91 98765 43210")
        == "+91 98765 43210"
    )


def test_normalize_phone_number_formats_valid_number():
    from lead_collector.extraction.fields import normalize_phone_number

    assert (
        normalize_phone_number("+1 (212) 867-5309")
        == "+1 212-867-5309"
    )


def test_normalize_phone_number_rejects_invalid_number():
    from lead_collector.extraction.fields import normalize_phone_number

    assert normalize_phone_number("+91 123") is None


def test_normalize_phone_number_rejects_malformed_input():
    from lead_collector.extraction.fields import normalize_phone_number

    assert normalize_phone_number("not a phone number") is None


def test_normalize_phone_number_handles_empty_input():
    from lead_collector.extraction.fields import normalize_phone_number

    assert normalize_phone_number("") is None


def test_get_phone_country():
    from lead_collector.extraction.fields import get_phone_country

    assert get_phone_country("+91 98765 43210") == "IN"
    assert get_phone_country("+1 (212) 867-5309") == "US"


def test_get_phone_country_rejects_invalid_number():
    from lead_collector.extraction.fields import get_phone_country

    assert get_phone_country("+91 123") is None


def test_get_phone_country_handles_empty_input():
    from lead_collector.extraction.fields import get_phone_country

    assert get_phone_country("") is None
    assert get_phone_country("   ") is None