import re
from urllib.parse import urlparse

import phonenumbers
from phonenumbers import NumberParseException


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


def extract_emails(text: str) -> list[str]:
    """Extract unique email addresses from text."""
    matches = EMAIL_PATTERN.findall(text)

    unique_emails: list[str] = []
    seen: set[str] = set()

    for email in matches:
        normalized = email.lower()

        if normalized not in seen:
            seen.add(normalized)
            unique_emails.append(normalized)

    return unique_emails


def extract_phone_numbers(text: str) -> list[str]:
    """Extract and validate phone numbers from text."""

    unique_numbers: list[str] = []
    seen: set[str] = set()

    for match in phonenumbers.PhoneNumberMatcher(text, None):
        number = match.number

        if not phonenumbers.is_possible_number(number):
            continue

        if not phonenumbers.is_valid_number(number):
            continue

        normalized = phonenumbers.format_number(
            number,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        )

        if normalized not in seen:
            seen.add(normalized)
            unique_numbers.append(normalized)

    return unique_numbers


def extract_linkedin_url(urls: list[str]) -> str | None:
    """Find the first LinkedIn profile or company URL."""
    for url in urls:
        try:
            parsed = urlparse(url)
        except ValueError:
            continue

        hostname = (parsed.hostname or "").lower()

        if hostname == "linkedin.com" or hostname.endswith(".linkedin.com"):
            return url

    return None