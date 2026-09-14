from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class ValidationStatus(str, Enum):
    """Possible validation states for a lead."""

    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"


class Lead(BaseModel):
    """Represents a business lead collected by the pipeline."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    id: UUID = Field(default_factory=uuid4)

    # Company information
    company_name: str = Field(min_length=1, max_length=200)
    website: HttpUrl | None = None
    industry: str | None = None

    # Location
    city: str | None = None
    state: str | None = None
    country: str | None = None

    # Contact information
    contact_name: str | None = None
    contact_role: str | None = None
    email: EmailStr | None = None
    phone: str | None = None

    # Online presence
    linkedin_url: HttpUrl | None = None
    source_url: HttpUrl | None = None

    # Pipeline metadata
    lead_score: int = Field(default=0, ge=0, le=100)
    validation_status: ValidationStatus = ValidationStatus.PENDING
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )