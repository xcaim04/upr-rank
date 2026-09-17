"""Unit tests for the bcrypt password hashing adapter."""

import pytest
from src.auth.infrastructure.password_hasher import BcryptPasswordHasher

pytestmark = pytest.mark.unit


def test_hash_password_is_one_way() -> None:
    hashed = BcryptPasswordHasher().hash_password("s3cret-pass")

    assert hashed != "s3cret-pass"
    assert hashed.startswith("$2")


def test_verify_password_with_matching_plaintext() -> None:
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash_password("s3cret-pass")

    assert hasher.verify_password("s3cret-pass", hashed) is True


def test_verify_password_with_wrong_plaintext() -> None:
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash_password("s3cret-pass")

    assert hasher.verify_password("wrong-pass", hashed) is False


def test_hashes_are_unique_even_for_same_password() -> None:
    hasher = BcryptPasswordHasher()

    assert hasher.hash_password("s3cret-pass") != hasher.hash_password("s3cret-pass")
