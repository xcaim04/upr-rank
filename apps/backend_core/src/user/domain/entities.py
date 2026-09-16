"""User domain entities and value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Role(StrEnum):
    """Available user roles inside UPR-RANK (RBAC)."""

    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


@dataclass(slots=True)
class User:
    """Pure domain entity representing a platform user.

    Carries no ORM or framework dependency: infrastructure adapters are
    responsible for mapping it to and from persistent storage.
    """

    email: str
    username: str
    hashed_password: str
    full_name: str
    role: Role = Role.STUDENT
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Normalize identity fields on entity creation."""
        self.email = self.email.strip().lower()
        self.username = self.username.strip().lower()
