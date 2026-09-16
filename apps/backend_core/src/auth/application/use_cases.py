"""Auth use cases (application services).

Each use case orchestrates ports and repositories, applying business rules.
They know nothing about HTTP, SQLAlchemy, or FastAPI.
"""

from __future__ import annotations

from src.auth.application.dtos import LoginInput, RegisterInput
from src.auth.application.errors import (
    AccountDisabledError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyRegisteredError,
)
from src.auth.application.ports import PasswordHasher
from src.user.application.ports import UserRepository
from src.user.domain.entities import Role, User


class RegisterUser:
    """Creates a student account, enforcing unique email/username."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        self._users = users
        self._hasher = hasher

    def execute(self, data: RegisterInput) -> User:
        if self._users.get_by_email(data.email) is not None:
            raise EmailAlreadyRegisteredError()
        if self._users.get_by_username(data.username) is not None:
            raise UsernameAlreadyRegisteredError()

        user = User(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=self._hasher.hash_password(data.password),
            role=Role.STUDENT,
        )
        self._users.add(user)
        return user


class LoginUser:
    """Authenticates a user by email and password."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        self._users = users
        self._hasher = hasher

    def execute(self, data: LoginInput) -> User:
        user = self._users.get_by_email(data.email)
        if user is None or not self._hasher.verify_password(
            data.password, user.hashed_password
        ):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise AccountDisabledError()
        return user
