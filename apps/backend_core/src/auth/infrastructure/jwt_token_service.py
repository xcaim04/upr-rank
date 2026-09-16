"""JWT token service adapter implementation.

Uses PyJWT (HS256) with the secret, algorithm and TTLs from application
settings. Access tokens are short-lived; refresh tokens last longer and are
distinguished by the ``type`` claim.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from src.auth.application.errors import ExpiredTokenError, InvalidTokenError
from src.auth.application.ports import TokenPayload, TokenProvider
from src.auth.domain.entities import TokenType
from src.shared.config import settings

_TOKEN_TYPE = "type"
_TOKEN_SUBJECT = "sub"
_TOKEN_ROLE = "role"


class JWTTokenProvider(TokenProvider):
    """Signs and validates JWT tokens using application settings."""

    def create_access_token(self, *, user_id: str, role: str) -> str:
        lifetime = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        return self._encode(
            user_id=user_id, role=role, token_type=TokenType.ACCESS, lifetime=lifetime
        )

    def create_refresh_token(self, *, user_id: str, role: str) -> str:
        lifetime = timedelta(days=settings.jwt_refresh_token_expire_days)
        return self._encode(
            user_id=user_id, role=role, token_type=TokenType.REFRESH, lifetime=lifetime
        )

    def decode_token(self, token: str) -> TokenPayload:
        try:
            data = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredTokenError() from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError() from exc

        return TokenPayload(
            user_id=data[_TOKEN_SUBJECT],
            role=data[_TOKEN_ROLE],
            token_type=TokenType(data[_TOKEN_TYPE]),
        )

    @staticmethod
    def _encode(
        *, user_id: str, role: str, token_type: TokenType, lifetime: timedelta
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            _TOKEN_SUBJECT: user_id,
            _TOKEN_ROLE: role,
            _TOKEN_TYPE: token_type.value,
            "iat": now,
            "exp": now + lifetime,
        }
        return jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
