"""SQLAlchemy implementation of the problem persistence port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.problem.application.ports import ProblemRepository
from src.problem.domain.entities import Difficulty, Problem
from src.problem.infrastructure.models import ProblemModel


class SQLAlchemyProblemRepository(ProblemRepository):
    """Maps :class:`Problem` domain objects to and from the ``problems`` table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, problem: Problem) -> None:
        self._session.add(self._to_model(problem))

    def get_by_id(self, problem_id: UUID) -> Problem | None:
        row = self._session.get(ProblemModel, problem_id)
        return self._to_domain(row)

    def get_by_slug(self, slug: str) -> Problem | None:
        row = self._session.scalar(
            select(ProblemModel).where(ProblemModel.slug == slug.strip().lower())
        )
        return self._to_domain(row)

    def list(
        self, *, visible_only: bool, offset: int = 0, limit: int = 50
    ) -> list[Problem]:
        statement = select(ProblemModel).order_by(ProblemModel.created_at)
        if visible_only:
            statement = statement.where(ProblemModel.is_visible.is_(True))
        rows = self._session.scalars(statement.offset(offset).limit(limit)).all()
        return [self._to_domain(row) for row in rows]  # type: ignore[arg-type]

    def update(self, problem: Problem) -> None:
        model = self._session.get(ProblemModel, problem.id)
        if model is None:
            self._session.add(self._to_model(problem))
            return
        model.title = problem.title
        model.slug = problem.slug
        model.statement = problem.statement
        model.difficulty = problem.difficulty.value
        model.time_limit_ms = problem.time_limit_ms
        model.memory_limit_mb = problem.memory_limit_mb
        model.is_visible = problem.is_visible

    def delete(self, problem_id: UUID) -> None:
        model = self._session.get(ProblemModel, problem_id)
        if model is not None:
            self._session.delete(model)

    @staticmethod
    def _to_model(problem: Problem) -> ProblemModel:
        return ProblemModel(
            id=problem.id,
            title=problem.title,
            slug=problem.slug,
            statement=problem.statement,
            difficulty=problem.difficulty.value,
            time_limit_ms=problem.time_limit_ms,
            memory_limit_mb=problem.memory_limit_mb,
            author_id=problem.author_id,
            is_visible=problem.is_visible,
        )

    @staticmethod
    def _to_domain(row: ProblemModel | None) -> Problem | None:
        if row is None:
            return None
        return Problem(
            id=row.id,
            title=row.title,
            slug=row.slug,
            statement=row.statement,
            difficulty=Difficulty(row.difficulty),
            time_limit_ms=row.time_limit_ms,
            memory_limit_mb=row.memory_limit_mb,
            author_id=row.author_id,
            is_visible=row.is_visible,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
