"""Shared pytest configuration for the backend tests."""

from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Make the backend src package importable when running tests from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.main import app  # noqa: E402
from src.shared.infrastructure.database import Base, get_db  # noqa: E402


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Create an in-memory SQLite session with a fresh schema per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient wired to the in-memory SQLite session."""

    def _override_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
