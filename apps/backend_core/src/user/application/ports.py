"""Application ports for the user module.

Ports (interfaces) invert the dependency direction: the domain/application
layer declares them and infrastructure adapters implement them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.user.domain.entities import User


class UserRepository(ABC):
    """Persistence port for :class:`User` aggregates."""

    @abstractmethod
    def add(self, user: User) -> None:
        """Persist a new user. Raises IntegrityError on duplicate keys."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given normalized email, if any."""

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Return the user with the given normalized username, if any."""

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """Return the user with the given id, if any."""

    @abstractmethod
    def list(self, offset: int = 0, limit: int = 50) -> list[User]:
        """Return a page of users (admin/management listing)."""
