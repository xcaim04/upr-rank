"""Unit tests for the RegisterUser use case."""

from uuid import UUID

import pytest
from src.auth.application.dtos import RegisterInput
from src.auth.application.errors import (
    EmailAlreadyRegisteredError,
    UsernameAlreadyRegisteredError,
)
from src.auth.application.ports import PasswordHasher
from src.auth.application.use_cases import RegisterUser
from src.user.application.ports import UserRepository
from src.user.domain.entities import Role, User

pytestmark = pytest.mark.unit


class FakeUserRepository(UserRepository):
    """In-memory double of the user persistence port."""

    def __init__(self) -> None:
        self._users: list[User] = []

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


class FakeHasher(PasswordHasher):
    """Double that records the raw password it hashed."""

    def __init__(self) -> None:
        self.hashed: list[str] = []

    def hash_password(self, raw_password: str) -> str:
        self.hashed.append(raw_password)
        return f"hashed:{raw_password}"

    def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        return f"hashed:{raw_password}" == hashed_password


@pytest.fixture()
def repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture()
def hasher() -> FakeHasher:
    return FakeHasher()


def _input(**overrides: object) -> RegisterInput:
    defaults: dict[str, object] = {
        "email": "student@upr.edu.cu",
        "username": "juanito",
        "full_name": "Juan Pérez",
        "password": "s3cret-pass",
    }
    defaults.update(overrides)
    return RegisterInput(**defaults)


def test_registers_a_student(
    repository: FakeUserRepository, hasher: FakeHasher
) -> None:
    user = RegisterUser(repository, hasher).execute(_input())

    assert user.email == "student@upr.edu.cu"
    assert user.role is Role.STUDENT
    assert user.is_active is True
    assert user.hashed_password.startswith("hashed:")
    assert len(repository._users) == 1
    assert hasher.hashed == ["s3cret-pass"]


def test_rejects_duplicate_email(
    repository: FakeUserRepository, hasher: FakeHasher
) -> None:
    RegisterUser(repository, hasher).execute(_input())

    with pytest.raises(EmailAlreadyRegisteredError):
        RegisterUser(repository, hasher).execute(_input(username="otro"))


def test_rejects_duplicate_username(
    repository: FakeUserRepository, hasher: FakeHasher
) -> None:
    RegisterUser(repository, hasher).execute(_input())

    with pytest.raises(UsernameAlreadyRegisteredError):
        RegisterUser(repository, hasher).execute(_input(email="otro@upr.edu.cu"))
