"""Unit tests for the LoginUser use case."""

from uuid import UUID

import pytest
from src.auth.application.dtos import LoginInput
from src.auth.application.errors import (
    AccountDisabledError,
    InvalidCredentialsError,
)
from src.auth.application.ports import PasswordHasher
from src.auth.application.use_cases import LoginUser
from src.user.application.ports import UserRepository
from src.user.domain.entities import Role, User

pytestmark = pytest.mark.unit


class StubUserRepository(UserRepository):
    """Double that serves a pre-seeded user."""

    def __init__(self, users: list[User]) -> None:
        self._users = users

    def add(self, user: User) -> None:
        self._users.append(user)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users if u.email == email.lower()), None)

    def get_by_username(self, username: str) -> User | None:
        return next((u for u in self._users if u.username == username.lower()), None)

    def get_by_id(self, user_id: UUID) -> User | None:
        return next((u for u in self._users if u.id == user_id), None)

    def list(self, offset: int = 0, limit: int = 50) -> list[User]:
        return self._users[offset : offset + limit]


class StubHasher(PasswordHasher):
    def __init__(self, plain_password: str) -> None:
        self._plain = plain_password

    def hash_password(self, raw_password: str) -> str:
        return f"hashed:{raw_password}"

    def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        return self.hash_password(raw_password) == hashed_password


def _user(*, is_active: bool = True, role: Role = Role.STUDENT) -> User:
    return User(
        email="student@upr.edu.cu",
        username="juanito",
        full_name="Juan Pérez",
        hashed_password="hashed:s3cret-pass",
        role=role,
        is_active=is_active,
    )


def test_login_with_valid_credentials() -> None:
    user = _user()
    use_case = LoginUser(StubUserRepository([user]), StubHasher("s3cret-pass"))

    result = use_case.execute(
        LoginInput(email="student@upr.edu.cu", password="s3cret-pass")
    )

    assert result is user


def test_login_with_wrong_password() -> None:
    use_case = LoginUser(StubUserRepository([_user()]), StubHasher("s3cret-pass"))

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(LoginInput(email="student@upr.edu.cu", password="nope"))


def test_login_with_unknown_email() -> None:
    use_case = LoginUser(StubUserRepository([_user()]), StubHasher("s3cret-pass"))

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(LoginInput(email="ghost@upr.edu.cu", password="s3cret-pass"))


def test_login_with_disabled_account() -> None:
    use_case = LoginUser(
        StubUserRepository([_user(is_active=False)]), StubHasher("s3cret-pass")
    )

    with pytest.raises(AccountDisabledError):
        use_case.execute(LoginInput(email="student@upr.edu.cu", password="s3cret-pass"))
