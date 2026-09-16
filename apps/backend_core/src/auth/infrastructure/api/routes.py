"""Auth API routes: register, login and token refresh."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from src.auth.application.dtos import LoginInput, RefreshInput, RegisterInput
from src.auth.application.errors import InvalidTokenError
from src.auth.application.ports import TokenProvider
from src.auth.application.use_cases import LoginUser, RegisterUser
from src.auth.domain.entities import TokenType
from src.auth.infrastructure.api.dependencies import get_current_user
from src.auth.infrastructure.api.schemas import AuthResponse, TokenResponse, UserOut
from src.auth.infrastructure.jwt_token_service import JWTTokenProvider
from src.auth.infrastructure.password_hasher import BcryptPasswordHasher
from src.shared.infrastructure.database import get_db
from src.user.domain.entities import User
from src.user.infrastructure.repository import SQLAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["auth"])

_DESCRIPTION = "UPR-RANK authentication and account management."


def _token_pair(user: User, provider: TokenProvider) -> AuthResponse:
    access = provider.create_access_token(user_id=str(user.id), role=user.role.value)
    refresh = provider.create_refresh_token(user_id=str(user.id), role=user.role.value)
    return AuthResponse(
        access_token=access, refresh_token=refresh, user=UserOut.from_domain(user)
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=201,
    summary="Register a new student account",
    description="Creates a student account and returns an authenticated token pair.",
)
def register(data: RegisterInput, db: Session = Depends(get_db)) -> AuthResponse:
    users = SQLAlchemyUserRepository(db)
    hasher = BcryptPasswordHasher()
    provider = JWTTokenProvider()
    user = RegisterUser(users, hasher).execute(data)
    db.commit()
    return _token_pair(user, provider)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email and password",
    description="Validates credentials and returns an authenticated token pair.",
    responses={401: {"description": "Invalid credentials or disabled account"}},
)
def login(data: LoginInput, db: Session = Depends(get_db)) -> AuthResponse:
    users = SQLAlchemyUserRepository(db)
    hasher = BcryptPasswordHasher()
    provider = JWTTokenProvider()
    user = LoginUser(users, hasher).execute(data)
    return _token_pair(user, provider)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh an access token",
    description="Issues a new access token from a valid refresh token.",
    responses={401: {"description": "Invalid or expired refresh token"}},
)
def refresh_token(data: RefreshInput, db: Session = Depends(get_db)) -> TokenResponse:
    provider = JWTTokenProvider()
    payload = provider.decode_token(data.refresh_token)
    if payload.token_type is not TokenType.REFRESH:
        raise InvalidTokenError()
    user = SQLAlchemyUserRepository(db).get_by_id(UUID(payload.user_id))
    if user is None or not user.is_active:
        raise InvalidTokenError()
    access = provider.create_access_token(user_id=str(user.id), role=user.role.value)
    return TokenResponse(access_token=access)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the current authenticated user",
    description="Returns the profile of the user owning the presented access token.",
    responses={401: {"description": "Missing, invalid or expired token"}},
)
def get_me(current_user: User = Security(get_current_user)) -> UserOut:
    return UserOut.from_domain(current_user)
