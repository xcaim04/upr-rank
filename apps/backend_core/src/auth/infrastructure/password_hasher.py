"""Bcrypt password hashing adapter implementation."""

from __future__ import annotations

from passlib.context import CryptContext
from src.auth.application.ports import PasswordHasher

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasher):
    """Hashes passwords with bcrypt using a cached passlib context."""

    def hash_password(self, raw_password: str) -> str:
        return _pwd_context.hash(raw_password)

    def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(raw_password, hashed_password)
