"""Response schemas for the problem API endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.problem.domain.entities import Problem


class ProblemOut(BaseModel):
    """Public representation of a problem returned by the API."""

    id: UUID
    title: str
    slug: str
    statement: str
    difficulty: str
    time_limit_ms: int
    memory_limit_mb: int
    author_id: UUID
    is_visible: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, problem: Problem) -> ProblemOut:
        return cls(
            id=problem.id,
            title=problem.title,
            slug=problem.slug,
            statement=problem.statement,
            difficulty=problem.difficulty.value,
            time_limit_ms=problem.time_limit_ms,
            memory_limit_mb=problem.memory_limit_mb,
            author_id=problem.author_id,
            is_visible=problem.is_visible,
            created_at=problem.created_at,
            updated_at=problem.updated_at,
        )
