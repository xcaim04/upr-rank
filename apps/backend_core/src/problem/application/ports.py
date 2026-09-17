"""Application ports for the problem module.

Ports (interfaces) invert the dependency direction: the domain/application
layer declares them and infrastructure adapters implement them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.problem.domain.entities import Problem


class ProblemRepository(ABC):
    """Persistence port for :class:`Problem` aggregates."""

    @abstractmethod
    def add(self, problem: Problem) -> None:
        """Persist a new problem. Raises IntegrityError on duplicate keys."""

    @abstractmethod
    def get_by_id(self, problem_id: UUID) -> Problem | None:
        """Return the problem with the given id, if any."""

    @abstractmethod
    def get_by_slug(self, slug: str) -> Problem | None:
        """Return the problem with the given normalized slug, if any."""

    @abstractmethod
    def list(
        self, *, visible_only: bool, offset: int = 0, limit: int = 50
    ) -> list[Problem]:
        """Return a page of problems, optionally only public ones."""

    @abstractmethod
    def update(self, problem: Problem) -> None:
        """Persist the changes made to an existing problem."""

    @abstractmethod
    def delete(self, problem_id: UUID) -> None:
        """Remove a problem by id (no-op when it does not exist)."""
