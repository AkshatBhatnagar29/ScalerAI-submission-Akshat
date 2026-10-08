from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models import HostedZone
from app.database.session import get_db
from app.main import app


TEST_DB = Path(__file__).parent / "test_route53.sqlite3"
engine = create_engine(f"sqlite:///{TEST_DB}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolated_database():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        test_client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        yield test_client


def test_unauthenticated_get_fails():
    assert TestClient(app).get("/api/hosted-zones").status_code == 401


def test_create_public_and_private_zones_and_server_created_user(client):
    public = client.post("/api/hosted-zones", json={"name": " Example.COM. ", "type": "PUBLIC"})
    private = client.post("/api/hosted-zones", json={"name": "internal.example.com", "type": "PRIVATE"})
    assert public.status_code == 201
    assert public.json()["name"] == "example.com"
    assert public.json()["created_by"] == "admin"
    assert private.status_code == 201


@pytest.mark.parametrize("payload", [{"type": "PUBLIC"}, {"name": "x.com", "type": "INVALID"}, {"name": "not a domain", "type": "PUBLIC"}])
def test_create_validation(client, payload):
    assert client.post("/api/hosted-zones", json=payload).status_code == 422


def test_duplicate_search_case_insensitive_and_empty_result(client):
    assert client.post("/api/hosted-zones", json={"name": "Example.com", "type": "PUBLIC"}).status_code == 201
    assert client.post("/api/hosted-zones", json={"name": "example.com.", "type": "PUBLIC"}).status_code == 409
    assert client.get("/api/hosted-zones?search=EXAMPLE").json()["total"] == 1
    assert client.get("/api/hosted-zones?search=missing").json()["items"] == []


def test_get_update_and_delete_preserve_immutable_fields(client):
    created = client.post("/api/hosted-zones", json={"name": "old.example.com", "type": "PUBLIC", "description": "old"}).json()
    zone_id = created["id"]
    updated = client.put(f"/api/hosted-zones/{zone_id}", json={"name": "new.example.com", "description": "new"})
    assert updated.status_code == 200
    body = updated.json()
    assert body["zone_id"] == created["zone_id"]
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] >= created["updated_at"]
    assert client.get(f"/api/hosted-zones/{zone_id}").status_code == 200
    assert client.delete(f"/api/hosted-zones/{zone_id}").status_code == 204
    assert client.get(f"/api/hosted-zones/{zone_id}").status_code == 404
    assert client.delete(f"/api/hosted-zones/{zone_id}").status_code == 404


def test_duplicate_update_and_unknown_zone(client):
    first = client.post("/api/hosted-zones", json={"name": "one.example.com", "type": "PUBLIC"}).json()
    second = client.post("/api/hosted-zones", json={"name": "two.example.com", "type": "PUBLIC"}).json()
    assert client.put(f"/api/hosted-zones/{second['id']}", json={"name": "one.example.com"}).status_code == 409
    assert client.get("/api/hosted-zones/99999").status_code == 404


def test_pagination_and_persistence(client):
    for index in range(5):
        assert client.post("/api/hosted-zones", json={"name": f"zone-{index}.example.com", "type": "PUBLIC"}).status_code == 201
    page = client.get("/api/hosted-zones?page=2&page_size=2").json()
    assert len(page["items"]) == 2
    assert page["total"] == 5
    assert page["total_pages"] == 3
    with TestingSessionLocal() as session:
        assert session.query(HostedZone).count() == 5
