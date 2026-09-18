import sqlite3
from pathlib import Path

from lead_collector.models import Lead
from lead_collector.processing.normalization import normalize_url


class LeadDatabase:
    """SQLite storage for lead records."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)

    def initialize(self) -> None:
        """Create and migrate the leads table."""

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
                    website_key TEXT,
                    industry TEXT,
                    city TEXT,
                    state TEXT,
                    country TEXT,
                    contact_name TEXT,
                    contact_role TEXT,
                    email TEXT,
                    phone TEXT,
                    phone_country TEXT,
                    linkedin_url TEXT,
                    source_url TEXT,
                    lead_score INTEGER NOT NULL,
                    validation_status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            self._migrate_database(connection)
            connection.commit()

    def _migrate_database(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        """Apply safe schema migrations to an existing database."""

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(leads)"
            ).fetchall()
        }

        if "website_key" not in columns:
            connection.execute(
                "ALTER TABLE leads ADD COLUMN website_key TEXT"
            )

        if "phone_country" not in columns:
            connection.execute(
                "ALTER TABLE leads ADD COLUMN phone_country TEXT"
            )

        self._backfill_website_keys(connection)
        self._remove_duplicate_websites(connection)

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_leads_website_key
            ON leads(website_key)
            """
        )

    @staticmethod
    def _backfill_website_keys(
        connection: sqlite3.Connection,
    ) -> None:
        """Populate website keys for existing records."""

        rows = connection.execute(
            """
            SELECT id, website
            FROM leads
            WHERE website IS NOT NULL
            """
        ).fetchall()

        for lead_id, website in rows:
            website_key = normalize_url(website)

            if website_key:
                connection.execute(
                    """
                    UPDATE leads
                    SET website_key = ?
                    WHERE id = ?
                    """,
                    (website_key, lead_id),
                )

    @staticmethod
    def _remove_duplicate_websites(
        connection: sqlite3.Connection,
    ) -> None:
        """Keep the newest record when duplicate websites exist."""

        duplicates = connection.execute(
            """
            SELECT website_key
            FROM leads
            WHERE website_key IS NOT NULL
            GROUP BY website_key
            HAVING COUNT(*) > 1
            """
        ).fetchall()

        for (website_key,) in duplicates:
            duplicate_ids = connection.execute(
                """
                SELECT id
                FROM leads
                WHERE website_key = ?
                ORDER BY created_at DESC
                """,
                (website_key,),
            ).fetchall()

            ids_to_delete = duplicate_ids[1:]

            for (lead_id,) in ids_to_delete:
                connection.execute(
                    "DELETE FROM leads WHERE id = ?",
                    (lead_id,),
                )

    def insert(self, lead: Lead) -> None:
        """
        Insert a lead or update an existing lead with the same website.
        """

        website = str(lead.website) if lead.website else None
        website_key = normalize_url(website) if website else None

        with sqlite3.connect(self._database_path) as connection:
            connection.execute(
                """
                INSERT INTO leads (
                    id,
                    company_name,
                    website,
                    website_key,
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(website_key)
                DO UPDATE SET
                    company_name = excluded.company_name,
                    website = excluded.website,
                    industry = COALESCE(
                        excluded.industry,
                        leads.industry
                    ),
                    city = COALESCE(
                        excluded.city,
                        leads.city
                    ),
                    state = COALESCE(
                        excluded.state,
                        leads.state
                    ),
                    country = COALESCE(
                        excluded.country,
                        leads.country
                    ),
                    contact_name = COALESCE(
                        excluded.contact_name,
                        leads.contact_name
                    ),
                    contact_role = COALESCE(
                        excluded.contact_role,
                        leads.contact_role
                    ),
                    email = COALESCE(
                        excluded.email,
                        leads.email
                    ),
                    phone = COALESCE(
                        excluded.phone,
                        leads.phone
                    ),
                    linkedin_url = COALESCE(
                        excluded.linkedin_url,
                        leads.linkedin_url
                    ),
                    source_url = COALESCE(
                        excluded.source_url,
                        leads.source_url
                    ),
                    lead_score = excluded.lead_score,
                    validation_status = excluded.validation_status
                """,
                (
                    str(lead.id),
                    lead.company_name,
                    website,
                    website_key,
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