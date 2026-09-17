"""Integration tests for the /auth API endpoints."""

from fastapi.testclient import TestClient

_REGISTER_PAYLOAD = {
    "email": "student@upr.edu.cu",
    "username": "juanito",
    "full_name": "Juan Pérez",
    "password": "s3cret-pass",
}


def _register(client: TestClient, **overrides: object) -> dict:
    payload = {**_REGISTER_PAYLOAD, **overrides}
    return client.post("/auth/register", json=payload).json()


def test_register_returns_tokens_and_user(client: TestClient) -> None:
    response = client.post("/auth/register", json=_REGISTER_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["email"] == "student@upr.edu.cu"
    assert body["user"]["username"] == "juanito"
    assert body["user"]["role"] == "student"
    assert body["user"]["is_active"] is True


def test_register_normalizes_email_and_username(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            **_REGISTER_PAYLOAD,
            "email": "  Student@UPR.Edu.Cu ",
            "username": " Juanito ",
        },
    )

    assert response.status_code == 201
    assert response.json()["user"]["email"] == "student@upr.edu.cu"
    assert response.json()["user"]["username"] == "juanito"


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    client.post("/auth/register", json=_REGISTER_PAYLOAD)

    response = client.post(
        "/auth/register", json={**_REGISTER_PAYLOAD, "username": "otro"}
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "email_registered",
        "message": "That email is already registered",
    }


def test_register_rejects_duplicate_username(client: TestClient) -> None:
    client.post("/auth/register", json=_REGISTER_PAYLOAD)

    response = client.post(
        "/auth/register", json={**_REGISTER_PAYLOAD, "email": "otro@upr.edu.cu"}
    )

    assert response.status_code == 409
    assert response.json()["code"] == "username_registered"


def test_register_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={**_REGISTER_PAYLOAD, "password": "short"},
    )

    assert response.status_code == 422


def test_login_returns_tokens(client: TestClient) -> None:
    _register(client)

    response = client.post(
        "/auth/login",
        json={"email": "student@upr.edu.cu", "password": "s3cret-pass"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["role"] == "student"


def test_login_with_wrong_password(client: TestClient) -> None:
    _register(client)

    response = client.post(
        "/auth/login",
        json={"email": "student@upr.edu.cu", "password": "wrong-pass"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


def test_login_with_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "ghost@upr.edu.cu", "password": "s3cret-pass"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


def test_refresh_rotates_access_token(client: TestClient) -> None:
    refresh = _register(client)["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh})

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_refresh_rejects_access_token(client: TestClient) -> None:
    access = _register(client)["access_token"]

    response = client.post("/auth/refresh", json={"refresh_token": access})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_refresh_rejects_garbage_token(client: TestClient) -> None:
    response = client.post(
        "/auth/refresh", json={"refresh_token": "not-a-real-token-token"}
    )

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_me_returns_current_user(client: TestClient) -> None:
    access = _register(client)["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})

    assert response.status_code == 200
    assert response.json()["email"] == "student@upr.edu.cu"
    assert response.json()["username"] == "juanito"


def test_me_without_token(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_me_with_refresh_token(client: TestClient) -> None:
    refresh = _register(client)["refresh_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {refresh}"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_me_with_garbage_token(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer garbage"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"
