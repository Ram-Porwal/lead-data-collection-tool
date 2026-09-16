import sqlite3
from pathlib import Path

from lead_collector.models import Lead


class LeadDatabase:
    """SQLite storage for lead records."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)

    def initialize(self) -> None:
        """Create the leads table if it does not already exist."""
        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with sqlite3.connect(self._database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    website TEXT,
                    industry TEXT,
                    city TEXT,
                    state TEXT,
                    country TEXT,
                    contact_name TEXT,
                    contact_role TEXT,
                    email TEXT,
                    phone TEXT,
                    linkedin_url TEXT,
                    source_url TEXT,
                    lead_score INTEGER NOT NULL,
                    validation_status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def insert(self, lead: Lead) -> None:
        """Insert a lead into the database."""
        with sqlite3.connect(self._database_path) as connection:
            connection.execute(
                """
                INSERT INTO leads (
                    id,
                    company_name,
                    website,
                    industry,
                    city,
                    state,
                    country,
                    contact_name,
                    contact_role,
                    email,
                    phone,
                    linkedin_url,
                    source_url,
                    lead_score,
                    validation_status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(lead.id),
                    lead.company_name,
                    str(lead.website) if lead.website else None,
                    lead.industry,
                    lead.city,
                    lead.state,
                    lead.country,
                    lead.contact_name,
                    lead.contact_role,
                    str(lead.email) if lead.email else None,
                    lead.phone,
                    str(lead.linkedin_url) if lead.linkedin_url else None,
                    str(lead.source_url) if lead.source_url else None,
                    lead.lead_score,
                    lead.validation_status.value,
                    lead.created_at.isoformat(),
                ),
            )

    def count(self) -> int:
        """Return the number of stored leads."""
        with sqlite3.connect(self._database_path) as connection:
            result = connection.execute(
                "SELECT COUNT(*) FROM leads"
            ).fetchone()

        return result[0] if result else 0