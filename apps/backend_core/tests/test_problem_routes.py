"""Integration tests for the problem API endpoints and RBAC."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.auth.infrastructure.jwt_token_service import JWTTokenProvider
from src.problem.domain.entities import Difficulty
from src.problem.infrastructure.repository import SQLAlchemyProblemRepository
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


def _seed_problem(
    client: TestClient, author: User, db: Session, **overrides: object
) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": "Suma de dos números",
        "statement": "Dados dos enteros, calcula su suma.",
        "difficulty": Difficulty.EASY,
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
    }
    payload.update(overrides)
    response = client.post("/problems", json=payload, headers=_bearer(author))
    assert response.status_code == 201
    body = response.json()
    return {
        "id": body["id"],
        "response": body,
    }


def test_create_problem_as_teacher(client: TestClient, db_session: Session) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )

    response = client.post(
        "/problems",
        json={
            "title": "Suma de dos números",
            "statement": "Dados dos enteros, calcula su suma.",
            "difficulty": Difficulty.EASY,
            "time_limit_ms": 1000,
            "memory_limit_mb": 256,
        },
        headers=_bearer(teacher),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["slug"] == "suma-de-dos-numeros"
    assert body["is_visible"] is False
    assert body["author_id"] == str(teacher.id)


def test_create_problem_as_student_is_forbidden(
    client: TestClient, db_session: Session
) -> None:
    student = _seed_user(
        db_session, email="student@upr.edu.cu", username="juanito", role=Role.STUDENT
    )

    response = client.post(
        "/problems",
        json={
            "title": "Suma de dos números",
            "statement": "Dados dos enteros, calcula su suma.",
            "difficulty": Difficulty.EASY,
            "time_limit_ms": 1000,
            "memory_limit_mb": 256,
        },
        headers=_bearer(student),
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_create_problem_with_duplicate_slug(
    client: TestClient, db_session: Session
) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    _seed_problem(client, teacher, db_session)

    response = client.post(
        "/problems",
        json={
            "title": "Otro título",
            "slug": "suma-de-dos-numeros",
            "statement": "Un enunciado totalmente distinto.",
            "difficulty": Difficulty.MEDIUM,
            "time_limit_ms": 2000,
            "memory_limit_mb": 512,
        },
        headers=_bearer(teacher),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "slug_registered"


def test_list_problems_as_student_only_shows_visible(
    client: TestClient, db_session: Session
) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    student = _seed_user(
        db_session, email="student@upr.edu.cu", username="juanito", role=Role.STUDENT
    )
    _seed_problem(client, teacher, db_session, title="Hola Mundo", slug="hola-mundo")
    _seed_problem(
        client,
        teacher,
        db_session,
        title="Divisible",
        slug="divisible",
        is_visible=True,
    )

    response = client.get("/problems", headers=_bearer(student))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["slug"] == "divisible"


def test_list_problems_as_admin_shows_all(
    client: TestClient, db_session: Session
) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    admin = _seed_user(
        db_session, email="admin@upr.edu.cu", username="admin", role=Role.ADMIN
    )
    _seed_problem(client, teacher, db_session, title="Hola Mundo", slug="hola-mundo")

    response = client.get("/problems", headers=_bearer(admin))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_visible_problem_as_student(
    client: TestClient, db_session: Session
) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    student = _seed_user(
        db_session, email="student@upr.edu.cu", username="juanito", role=Role.STUDENT
    )
    problem = _seed_problem(
        client,
        teacher,
        db_session,
        title="Divisible",
        slug="divisible",
        is_visible=True,
    )

    response = client.get(f"/problems/{problem['id']}", headers=_bearer(student))

    assert response.status_code == 200
    assert response.json()["title"] == "Divisible"


def test_get_hidden_problem_as_student_is_not_found(
    client: TestClient, db_session: Session
) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    student = _seed_user(
        db_session, email="student@upr.edu.cu", username="juanito", role=Role.STUDENT
    )
    problem = _seed_problem(client, teacher, db_session, title="Oculto", slug="oculto")

    response = client.get(f"/problems/{problem['id']}", headers=_bearer(student))

    assert response.status_code == 404
    assert response.json()["code"] == "problem_not_found"


def test_get_hidden_problem_as_teacher(client: TestClient, db_session: Session) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    problem = _seed_problem(client, teacher, db_session, title="Oculto", slug="oculto")

    response = client.get(f"/problems/{problem['id']}", headers=_bearer(teacher))

    assert response.status_code == 200


def test_get_problem_not_found(client: TestClient, db_session: Session) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )

    response = client.get(
        "/problems/99999999-9999-4999-8999-999999999999", headers=_bearer(teacher)
    )

    assert response.status_code == 404
    assert response.json()["code"] == "problem_not_found"


def test_update_own_problem_as_teacher(client: TestClient, db_session: Session) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    problem = _seed_problem(client, teacher, db_session)

    response = client.patch(
        f"/problems/{problem['id']}",
        json={"title": "Suma avanzada", "is_visible": True},
        headers=_bearer(teacher),
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Suma avanzada"
    assert response.json()["is_visible"] is True
    assert response.json()["slug"] == "suma-de-dos-numeros"


def test_update_someone_elses_problem_as_teacher_is_forbidden(
    client: TestClient, db_session: Session
) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    other = _seed_user(
        db_session, email="other@upr.edu.cu", username="other", role=Role.TEACHER
    )
    problem = _seed_problem(client, teacher, db_session)

    response = client.patch(
        f"/problems/{problem['id']}",
        json={"title": "Título ajeno"},
        headers=_bearer(other),
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_update_any_problem_as_admin(client: TestClient, db_session: Session) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    admin = _seed_user(
        db_session, email="admin@upr.edu.cu", username="admin", role=Role.ADMIN
    )
    problem = _seed_problem(client, teacher, db_session)

    response = client.patch(
        f"/problems/{problem['id']}",
        json={"is_visible": True},
        headers=_bearer(admin),
    )

    assert response.status_code == 200
    assert response.json()["is_visible"] is True


def test_delete_problem_as_admin(client: TestClient, db_session: Session) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    admin = _seed_user(
        db_session, email="admin@upr.edu.cu", username="admin", role=Role.ADMIN
    )
    problem = _seed_problem(client, teacher, db_session)

    response = client.delete(f"/problems/{problem['id']}", headers=_bearer(admin))

    assert response.status_code == 204
    deleted = SQLAlchemyProblemRepository(db_session).get_by_slug("suma-de-dos-numeros")
    assert deleted is None


def test_delete_problem_as_teacher_is_forbidden(
    client: TestClient, db_session: Session
) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )
    problem = _seed_problem(client, teacher, db_session)

    response = client.delete(f"/problems/{problem['id']}", headers=_bearer(teacher))

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_problem_routes_without_token(client: TestClient) -> None:
    assert client.get("/problems").status_code == 401
    assert client.post("/problems", json={}).status_code == 401


def test_problem_routes_with_refresh_token(
    client: TestClient, db_session: Session
) -> None:
    teacher = _seed_user(
        db_session, email="teacher@upr.edu.cu", username="teacher", role=Role.TEACHER
    )

    response = client.get("/problems", headers=_bearer(teacher, refresh=True))

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"
