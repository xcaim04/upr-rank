"""Input DTOs (Pydantic) used by the problem use cases.

Pydantic validates and normalizes raw HTTP payloads; the use cases then apply
business rules. No framework types leak into the domain layer.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from src.problem.domain.entities import Difficulty

_SLUG_PATTERN = r"^[a-z0-9][a-z0-9-]{0,199}$"

_VALID_SLUG = "Lowercase slug with digits and hyphens (also used in URLs)"


class CreateProblemInput(BaseModel):
    """Payload for creating a new problem."""

    title: str = Field(min_length=3, max_length=200, description="Problem title")
    slug: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
        pattern=_SLUG_PATTERN,
        description=(
            f"Optional URL slug; derived from the title when omitted. " f"{_VALID_SLUG}"
        ),
    )
    statement: str = Field(min_length=10, description="Problem statement (Markdown)")
    difficulty: Difficulty = Field(description="Estimated problem complexity")
    time_limit_ms: int = Field(
        ge=100, le=30_000, description="Time limit in milliseconds"
    )
    memory_limit_mb: int = Field(ge=4, le=4096, description="Memory limit in megabytes")
    is_visible: bool = Field(
        default=False, description="Whether students can already see the problem"
    )

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return value.strip()

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()


class UpdateProblemInput(BaseModel):
    """Optional payload for updating an existing problem (PATCH semantics)."""

    title: str | None = Field(default=None, min_length=3, max_length=200)
    slug: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
        pattern=_SLUG_PATTERN,
        description=_VALID_SLUG,
    )
    statement: str | None = Field(default=None, min_length=10)
    difficulty: Difficulty | None = None
    time_limit_ms: int | None = Field(default=None, ge=100, le=30_000)
    memory_limit_mb: int | None = Field(default=None, ge=4, le=4096)
    is_visible: bool | None = None

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()
