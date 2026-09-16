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
    Call us at +91 98765 43210 or +1 (555) 123-4567.
    """

    result = extract_phone_numbers(text)

    assert result == [
        "+91 98765 43210",
        "+1 (555) 123-4567",
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