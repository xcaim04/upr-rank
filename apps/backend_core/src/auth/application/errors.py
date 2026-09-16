"""Application-layer errors for the auth and user modules."""

from __future__ import annotations

from src.shared.domain.errors import ApplicationError


class AuthenticationError(ApplicationError):
    """Base class for authentication failures (HTTP 401)."""

    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(status_code=401, code=code, message=message)


class InvalidCredentialsError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__(
            code="invalid_credentials", message="Email or password is incorrect"
        )


class AccountDisabledError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__(code="account_disabled", message="This account is disabled")


class InvalidTokenError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__(
            code="invalid_token", message="The token is invalid or malformed"
        )


class ExpiredTokenError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__(code="token_expired", message="The token has expired")


class ForbiddenError(ApplicationError):
    """Raised when the current user lacks permission (HTTP 403)."""

    def __init__(self) -> None:
        super().__init__(
            status_code=403, code="forbidden", message="You do not have permission"
        )


class EmailAlreadyRegisteredError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            code="email_registered",
            message="That email is already registered",
        )


class UsernameAlreadyRegisteredError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            code="username_registered",
            message="That username is already taken",
        )


class UserNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            status_code=404, code="user_not_found", message="User not found"
        )
