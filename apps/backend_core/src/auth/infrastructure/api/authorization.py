"""Role-based authorization dependency for protected routes.

``require_roles`` is a dependency factory meant to be used through FastAPI's
``Security``, so the allowed roles are also exposed to the OpenAPI docs:
    Security(require_roles(Role.ADMIN))
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Security
from src.auth.application.errors import ForbiddenError
from src.auth.infrastructure.api.dependencies import get_current_user
from src.user.domain.entities import Role, User


def require_roles(*roles: Role) -> Callable[[User], User]:
    """Return a dependency that only lets users with one of ``roles`` through."""

    allowed = set(roles)

    def check(current_user: User = Security(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise ForbiddenError()
        return current_user

    return check
