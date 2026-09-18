import sqlite3
from datetime import datetime
from uuid import UUID

from lead_collector.models import Lead, ValidationStatus


class LeadRepository:
    """Repository for reading Lead objects from SQLite."""

    def __init__(self, database_path: str) -> None:
        self._database_path = database_path

    def get_by_id(self, lead_id: UUID) -> Lead | None:
        """Return a lead by ID, or None if it does not exist."""

        with sqlite3.connect(self._database_path) as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                "SELECT * FROM leads WHERE id = ?",
                (str(lead_id),),
            ).fetchone()

        return self._row_to_lead(row) if row else None

    def get_all(self) -> list[Lead]:
        """Return all stored leads."""

        with sqlite3.connect(self._database_path) as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                "SELECT * FROM leads ORDER BY created_at"
            ).fetchall()

        return [self._row_to_lead(row) for row in rows]

    def get_valid_leads(self) -> list[Lead]:
        """Return only leads marked as valid."""

        with sqlite3.connect(self._database_path) as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                """
                SELECT *
                FROM leads
                WHERE validation_status = ?
                ORDER BY lead_score DESC
                """,
                (ValidationStatus.VALID.value,),
            ).fetchall()

        return [self._row_to_lead(row) for row in rows]

    @staticmethod
    def _row_to_lead(row: sqlite3.Row) -> Lead:
        """Convert a SQLite row into a Lead object."""

        return Lead(
            id=UUID(row["id"]),
            company_name=row["company_name"],
            website=row["website"],
            industry=row["industry"],
            city=row["city"],
            state=row["state"],
            country=row["country"],
            contact_name=row["contact_name"],
            contact_role=row["contact_role"],
            email=row["email"],
            phone=row["phone"],
            phone_country=row["phone_country"],
            linkedin_url=row["linkedin_url"],
            source_url=row["source_url"],
            lead_score=row["lead_score"],
            validation_status=ValidationStatus(
                row["validation_status"]
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
        )