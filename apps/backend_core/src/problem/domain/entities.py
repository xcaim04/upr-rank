"""Problem domain entities and value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Difficulty(StrEnum):
    """Estimated complexity of a problem."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(slots=True)
class Problem:
    """Pure domain entity representing an algorithmic problem.

    Carries no ORM or framework dependency: infrastructure adapters are
    responsible for mapping it to and from persistent storage.
    """

    title: str
    slug: str
    statement: str
    difficulty: Difficulty
    time_limit_ms: int
    memory_limit_mb: int
    author_id: UUID
    is_visible: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Normalize identity fields on entity creation."""
        self.title = self.title.strip()
        self.slug = self.slug.strip().lower()
