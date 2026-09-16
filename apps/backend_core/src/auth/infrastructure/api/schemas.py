"""Response schemas for the auth API endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from src.user.domain.entities import User


class UserOut(BaseModel):
    """Public representation of a user returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, user: User) -> UserOut:
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )


class AuthResponse(BaseModel):
    """Tokens plus the authenticated user, returned on register/login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenResponse(BaseModel):
    """Fresh access token returned by the refresh endpoint."""

    access_token: str
    token_type: str = "bearer"
