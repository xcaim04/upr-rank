"""auth module domain entities and value objects."""

from __future__ import annotations

from enum import StrEnum


class TokenType(StrEnum):
    """Kind of JWT token issued by UPR-RANK."""

    ACCESS = "access"
    REFRESH = "refresh"
