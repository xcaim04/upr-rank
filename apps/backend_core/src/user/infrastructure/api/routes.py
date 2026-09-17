"""User management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from src.auth.infrastructure.api.authorization import require_roles
from src.auth.infrastructure.api.schemas import UserOut
from src.shared.infrastructure.database import get_db
from src.user.domain.entities import Role, User
from src.user.infrastructure.repository import SQLAlchemyUserRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=list[UserOut],
    summary="List all users (admin only)",
    description="Returns all registered users. Restricted to administrators.",
    responses={403: {"description": "The caller role lacks permission"}},
)
def list_users(
    _: User = Security(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
) -> list[UserOut]:
    users = SQLAlchemyUserRepository(db).list()
    return [UserOut.from_domain(user) for user in users]
