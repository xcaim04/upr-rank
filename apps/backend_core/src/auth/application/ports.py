"""Application ports for the auth module.

Ports declare what the auth use cases need so that infrastructure adapters
(PasswordHasher, TokenProvider) can be swapped without touching business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.auth.domain.entities import TokenType


class PasswordHasher(ABC):
    """Port for one-way password hashing and verification."""

    @abstractmethod
    def hash_password(self, raw_password: str) -> str:
        """Return a securely hashed representation of the raw password."""

    @abstractmethod
    def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        """Return True when the raw password matches the stored hash."""


class TokenPayload:
    """Decoded JWT claims used by the authentication layer."""

    def __init__(self, *, user_id: str, role: str, token_type: TokenType) -> None:
        self.user_id = user_id
        self.role = role
        self.token_type = token_type


class TokenProvider(ABC):
    """Port for issuing and validating signed JWT tokens."""

    @abstractmethod
    def create_access_token(self, *, user_id: str, role: str) -> str:
        """Issue a short-lived signed access token."""

    @abstractmethod
    def create_refresh_token(self, *, user_id: str, role: str) -> str:
        """Issue a long-lived signed refresh token."""

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload:
        """Validate a JWT signature and expiry, returning its payload.

        Raises an ``AuthenticationError`` when the token is invalid or expired.
        """
