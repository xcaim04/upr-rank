"""Problem use cases (application services).

Each use case orchestrates ports and repositories, applying business rules.
They know nothing about HTTP, SQLAlchemy, or FastAPI.
"""

from __future__ import annotations

import re
import unicodedata
from uuid import UUID

from src.problem.application.dtos import CreateProblemInput, UpdateProblemInput
from src.problem.application.errors import ProblemNotFoundError, SlugAlreadyExistsError
from src.problem.application.ports import ProblemRepository
from src.problem.domain.entities import Problem

_MAX_SLUG_LENGTH = 200


def _slugify(title: str) -> str:
    """Derive an ASCII lowercase URL slug from a title."""
    ascii_text = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug[:_MAX_SLUG_LENGTH] or "problem"


class CreateProblem:
    """Creates a problem, enforcing a unique slug."""

    def __init__(self, problems: ProblemRepository) -> None:
        self._problems = problems

    def execute(self, data: CreateProblemInput, *, author_id: UUID) -> Problem:
        slug = data.slug or _slugify(data.title)
        if self._problems.get_by_slug(slug) is not None:
            raise SlugAlreadyExistsError()

        problem = Problem(
            title=data.title,
            slug=slug,
            statement=data.statement,
            difficulty=data.difficulty,
            time_limit_ms=data.time_limit_ms,
            memory_limit_mb=data.memory_limit_mb,
            author_id=author_id,
            is_visible=data.is_visible,
        )
        self._problems.add(problem)
        return problem


class GetProblem:
    """Returns a problem by id or raises when it does not exist."""

    def __init__(self, problems: ProblemRepository) -> None:
        self._problems = problems

    def execute(self, problem_id: UUID) -> Problem:
        problem = self._problems.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()
        return problem


class ListProblems:
    """Returns a page of problems, optionally limited to public ones."""

    def __init__(self, problems: ProblemRepository) -> None:
        self._problems = problems

    def execute(
        self, *, visible_only: bool, offset: int = 0, limit: int = 50
    ) -> list[Problem]:
        return self._problems.list(
            visible_only=visible_only, offset=offset, limit=limit
        )


class UpdateProblem:
    """Applies a partial update to an existing problem."""

    def __init__(self, problems: ProblemRepository) -> None:
        self._problems = problems

    def execute(self, problem_id: UUID, data: UpdateProblemInput) -> Problem:
        problem = self._problems.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()

        if data.title is not None:
            problem.title = data.title
        if data.slug is not None:
            new_slug = data.slug
            if (
                new_slug != problem.slug
                and self._problems.get_by_slug(new_slug) is not None
            ):
                raise SlugAlreadyExistsError()
            problem.slug = new_slug
        if data.statement is not None:
            problem.statement = data.statement
        if data.difficulty is not None:
            problem.difficulty = data.difficulty
        if data.time_limit_ms is not None:
            problem.time_limit_ms = data.time_limit_ms
        if data.memory_limit_mb is not None:
            problem.memory_limit_mb = data.memory_limit_mb
        if data.is_visible is not None:
            problem.is_visible = data.is_visible

        self._problems.update(problem)
        return problem


class DeleteProblem:
    """Removes a problem by id or raises when it does not exist."""

    def __init__(self, problems: ProblemRepository) -> None:
        self._problems = problems

    def execute(self, problem_id: UUID) -> None:
        problem = self._problems.get_by_id(problem_id)
        if problem is None:
            raise ProblemNotFoundError()
        self._problems.delete(problem_id)
