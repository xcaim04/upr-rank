"""Unit tests for the JWT token provider adapter."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from src.auth.application.errors import ExpiredTokenError, InvalidTokenError
from src.auth.domain.entities import TokenType
from src.auth.infrastructure.jwt_token_service import JWTTokenProvider
from src.shared.config import settings

pytestmark = pytest.mark.unit


@pytest.fixture()
def provider() -> JWTTokenProvider:
    return JWTTokenProvider()


def _encode_token(*, user_id: str, role: str, token_type: TokenType) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "type": token_type.value,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=5),
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def test_create_access_token_payload(provider: JWTTokenProvider) -> None:
    token = provider.create_access_token(user_id="user-123", role="student")

    payload = provider.decode_token(token)
    assert payload.user_id == "user-123"
    assert payload.role == "student"
    assert payload.token_type is TokenType.ACCESS


def test_create_refresh_token_payload(provider: JWTTokenProvider) -> None:
    token = provider.create_refresh_token(user_id="user-123", role="student")

    payload = provider.decode_token(token)
    assert payload.user_id == "user-123"
    assert payload.token_type is TokenType.REFRESH


def test_access_and_refresh_tokens_are_distinct(provider: JWTTokenProvider) -> None:
    access = provider.create_access_token(user_id="user-123", role="student")
    refresh = provider.create_refresh_token(user_id="user-123", role="student")

    assert access != refresh
    assert (
        provider.decode_token(access).token_type
        is not provider.decode_token(refresh).token_type
    )


def test_decode_expired_token_raises(
    provider: JWTTokenProvider, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "jwt_access_token_expire_minutes", -5)

    token = provider.create_access_token(user_id="user-123", role="student")

    with pytest.raises(ExpiredTokenError):
        provider.decode_token(token)


def test_decode_tampered_token_raises(
    provider: JWTTokenProvider, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "jwt_secret_key", "other-secret")
    token = provider.create_access_token(user_id="user-123", role="student")

    with pytest.raises(InvalidTokenError):
        provider.decode_token(token + "tampered")


def test_decode_well_signed_token_from_any_secret(
    provider: JWTTokenProvider,
) -> None:
    token = _encode_token(
        user_id="user-999", role="admin", token_type=TokenType.REFRESH
    )

    payload = provider.decode_token(token)
    assert payload.user_id == "user-999"
    assert payload.role == "admin"
    assert payload.token_type is TokenType.REFRESH
