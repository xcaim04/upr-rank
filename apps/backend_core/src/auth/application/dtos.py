"""Input DTOs (Pydantic) used by the auth use cases.

Pydantic validates and normalizes raw HTTP payloads; the use cases then apply
business rules. No framework types leak into the domain layer.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class RefreshInput(BaseModel):
    """Payload for rotating an access token from a refresh token."""

    refresh_token: str = Field(min_length=10, description="Valid refresh token")


class RegisterInput(BaseModel):
    """Payload for creating a new student account."""

    email: EmailStr = Field(description="User email (login identifier)")
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-z0-9_]{3,30}$",
        description="Lowercase alphanumeric username with underscores",
    )
    full_name: str = Field(min_length=2, max_length=120, description="Display name")
    password: str = Field(
        min_length=8,
        max_length=72,
        description="Password (bcrypt limit is 72 bytes)",
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip().lower()


class LoginInput(BaseModel):
    """Payload for authenticating an existing user."""

    email: EmailStr = Field(description="Registered email")
    password: str = Field(description="Plain password to verify")

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()
