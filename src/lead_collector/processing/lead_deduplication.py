from collections.abc import Iterable

from lead_collector.models import Lead
from lead_collector.processing.normalization import normalize_url


def _normalize_email(email: str | None) -> str | None:
    """Normalize an email address for identity comparison."""

    if not email:
        return None

    normalized = email.strip().lower()

    return normalized or None


def _get_identity_keys(lead: Lead) -> set[str]:
    """Return strong identity keys for a lead."""

    keys: set[str] = set()

    if lead.website:
        normalized_website = normalize_url(str(lead.website))

        if normalized_website:
            keys.add(f"website:{normalized_website}")

    if lead.email:
        normalized_email = _normalize_email(str(lead.email))

        if normalized_email:
            keys.add(f"email:{normalized_email}")

    return keys


def deduplicate_leads(
    leads: Iterable[Lead],
) -> list[Lead]:
    """Remove duplicate leads using strong identity signals."""

    unique_leads: list[Lead] = []
    seen_keys: set[str] = set()

    for lead in leads:
        identity_keys = _get_identity_keys(lead)

        if identity_keys and identity_keys & seen_keys:
            continue

        unique_leads.append(lead)
        seen_keys.update(identity_keys)

    return unique_leads