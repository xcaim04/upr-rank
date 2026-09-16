"""Shared application error base type.

Domain/application layers raise typed errors; adapters map them to HTTP
responses via a single exception handler so controllers stay thin.
"""

from __future__ import annotations


class ApplicationError(Exception):
    """Base class for all business errors raised by use cases and ports."""

    def __init__(self, *, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)
