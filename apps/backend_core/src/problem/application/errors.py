"""Application-layer errors for the problem module."""

from __future__ import annotations

from src.shared.domain.errors import ApplicationError


class ProblemNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            status_code=404, code="problem_not_found", message="Problem not found"
        )


class SlugAlreadyExistsError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            status_code=409, code="slug_registered", message="That slug is already used"
        )
