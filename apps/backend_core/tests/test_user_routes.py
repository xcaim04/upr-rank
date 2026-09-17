"""Integration tests for protected user routes and RBAC."""

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.auth.infrastructure.jwt_token_service import JWTTokenProvider
from src.user.domain.entities import Role, User
from src.user.infrastructure.repository import SQLAlchemyUserRepository


def _seed_user(db: Session, *, email: str, username: str, role: Role) -> User:
    user = User(
        email=email,
        username=username,
        full_name="Test User",
        hashed_password="hashed:whatever",
        role=role,
    )
    SQLAlchemyUserRepository(db).add(user)
    db.commit()
    return user


def _bearer(user: User, *, refresh: bool = False) -> dict[str, str]:
    provider = JWTTokenProvider()
    if refresh:
        token = provider.create_refresh_token(
            user_id=str(user.id), role=user.role.value
        )
    else:
        token = provider.create_access_token(user_id=str(user.id), role=user.role.value)
    return {"Authorization": f"Bearer {token}"}


def test_list_users_as_admin(client: TestClient, db_session: Session) -> None:
    _seed_user(
        db_session,
        email="admin@upr.edu.cu",
        username="admin",
        role=Role.ADMIN,
    )
    _seed_user(
        db_session,
        email="student@upr.edu.cu",
        username="juanito",
        role=Role.STUDENT,
    )
    admin = SQLAlchemyUserRepository(db_session).get_by_email("admin@upr.edu.cu")
    assert admin is not None

    response = client.get("/users", headers=_bearer(admin))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {user["username"] for user in body} == {"admin", "juanito"}
    assert "hashed_password" not in body[0]


def test_list_users_as_student_is_forbidden(
    client: TestClient, db_session: Session
) -> None:
    student = _seed_user(
        db_session,
        email="student@upr.edu.cu",
        username="juanito",
        role=Role.STUDENT,
    )

    response = client.get("/users", headers=_bearer(student))

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_list_users_without_token(client: TestClient) -> None:
    response = client.get("/users")

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_list_users_with_refresh_token(client: TestClient, db_session: Session) -> None:
    admin = _seed_user(
        db_session, email="admin@upr.edu.cu", username="admin", role=Role.ADMIN
    )

    response = client.get("/users", headers=_bearer(admin, refresh=True))

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_list_users_rejects_unknown_subject(
    client: TestClient, db_session: Session
) -> None:
    ghost = User(
        email="ghost@upr.edu.cu",
        username="ghost",
        full_name="Ghost",
        hashed_password="hashed:x",
        role=Role.ADMIN,
        id=UUID("00000000-0000-4000-8000-000000000001"),
    )

    response = client.get("/users", headers=_bearer(ghost))

    assert response.status_code == 401
