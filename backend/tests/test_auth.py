from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_rejects_invalid_username() -> None:
    response = client.post("/api/auth/login", json={"username": "wrong", "password": "admin123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password."


def test_login_rejects_invalid_password() -> None:
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_me_requires_a_session() -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_login_me_logout_invalidates_session() -> None:
    login_response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_response.status_code == 200
    assert login_response.json() == {"authenticated": True, "user": {"username": "admin"}}
    assert "httponly" in login_response.headers["set-cookie"].lower()
    assert "admin123" not in login_response.text

    assert client.get("/api/auth/me").json() == {"authenticated": True, "user": {"username": "admin"}}
    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.json() == {"authenticated": False}
    assert client.get("/api/auth/me").status_code == 401
