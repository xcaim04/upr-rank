"""Authentication dependencies for protected routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.auth.application.errors import ExpiredTokenError, InvalidTokenError
from src.auth.domain.entities import TokenType
from src.auth.infrastructure.jwt_token_service import JWTTokenProvider
from src.shared.infrastructure.database import get_db
from src.user.domain.entities import User
from src.user.infrastructure.repository import SQLAlchemyUserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated :class:`User` from the Bearer access token.

    Raises an ``ApplicationError`` (mapped to HTTP 401) for missing, invalid,
    expired or non-access tokens, and for unknown or disabled accounts.
    """
    if credentials is None:
        raise InvalidTokenError()

    provider = JWTTokenProvider()
    try:
        payload = provider.decode_token(credentials.credentials)
    except (InvalidTokenError, ExpiredTokenError):
        raise InvalidTokenError() from None

    if payload.token_type is not TokenType.ACCESS:
        raise InvalidTokenError()

    user = SQLAlchemyUserRepository(db).get_by_id(UUID(payload.user_id))
    if user is None or not user.is_active:
        raise InvalidTokenError()
    return user
