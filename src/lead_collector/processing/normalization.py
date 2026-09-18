from urllib.parse import urlsplit, urlunsplit


def normalize_url(url: str) -> str:
    """Normalize a URL for consistent comparison and deduplication."""
    url = url.strip()

    if not url:
        return ""

    parts = urlsplit(url)

    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()

    # Remove default ports.
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    elif netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    # Remove trailing slash from paths, except for the root path.
    path = parts.path.rstrip("/") or "/"

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            parts.query,
            "",  # Fragments are ignored for deduplication.
        )
    )


COUNTRY_ALIASES = {
    "IN": "India",
    "IND": "India",
    "INDIA": "India",
    "US": "United States",
    "USA": "United States",
    "UNITED STATES": "United States",
    "UK": "United Kingdom",
    "GB": "United Kingdom",
    "GBR": "United Kingdom",
    "UNITED KINGDOM": "United Kingdom",
    "UAE": "United Arab Emirates",
    "AE": "United Arab Emirates",
    "ARE": "United Arab Emirates",
}


def normalize_country(country: str | None) -> str | None:
    """Normalize common country codes and name variants."""

    if not country:
        return None

    normalized = country.strip()

    if not normalized:
        return None

    return COUNTRY_ALIASES.get(
        normalized.upper(),
        normalized,
    )