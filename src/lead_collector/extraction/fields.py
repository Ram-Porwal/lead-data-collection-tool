import re
from urllib.parse import urlparse


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"
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
    """Extract likely phone numbers from text."""
    matches = PHONE_PATTERN.findall(text)

    unique_numbers: list[str] = []
    seen: set[str] = set()

    for number in matches:
        normalized = re.sub(r"\s+", " ", number).strip()

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