"""SQLAlchemy implementation of the user persistence port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.user.application.ports import UserRepository
from src.user.domain.entities import Role, User
from src.user.infrastructure.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """Maps :class:`User` domain objects to and from the ``users`` table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(self._to_model(user))

    def get_by_email(self, email: str) -> User | None:
        row = self._session.scalar(
            select(UserModel).where(UserModel.email == email.strip().lower())
        )
        return self._to_domain(row)

    def get_by_username(self, username: str) -> User | None:
        row = self._session.scalar(
            select(UserModel).where(UserModel.username == username.strip().lower())
        )
        return self._to_domain(row)

    def get_by_id(self, user_id: UUID) -> User | None:
        row = self._session.get(UserModel, user_id)
        return self._to_domain(row)

    def list(self, offset: int = 0, limit: int = 50) -> list[User]:
        rows = self._session.scalars(
            select(UserModel).order_by(UserModel.created_at).offset(offset).limit(limit)
        ).all()
        return [self._to_domain(row) for row in rows]  # type: ignore[arg-type]

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            role=user.role.value,
            is_active=user.is_active,
        )

    @staticmethod
    def _to_domain(row: UserModel | None) -> User | None:
        if row is None:
            return None
        return User(
            id=row.id,
            email=row.email,
            username=row.username,
            full_name=row.full_name,
            hashed_password=row.hashed_password,
            role=Role(row.role),
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
