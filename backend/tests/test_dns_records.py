from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app


TEST_DB = Path(__file__).parent / "test_records.sqlite3"
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


def make_zone(client: TestClient, name: str = "example.com") -> dict:
    return client.post("/api/hosted-zones", json={"name": name, "type": "PUBLIC"}).json()


def test_records_are_scoped_and_counted(client):
    zone = make_zone(client)
    other = make_zone(client, "other.example.com")
    payload = {"name": "www.example.com", "type": "A", "ttl": 300, "value": "192.0.2.1"}
    created = client.post(f"/api/hosted-zones/{zone['id']}/records", json=payload)
    assert created.status_code == 201
    assert client.get(f"/api/hosted-zones/{zone['id']}/records").json()["total"] == 1
    assert client.get(f"/api/hosted-zones/{other['id']}/records").json()["total"] == 0
    assert client.get(f"/api/hosted-zones/{other['id']}/records/{created.json()['id']}").status_code == 404
    assert client.get(f"/api/hosted-zones/{zone['id']}").json()["record_count"] == 1


@pytest.mark.parametrize("record_type,payload", [
    ("A", {"value": "192.0.2.10"}),
    ("AAAA", {"value": "2001:db8::10"}),
    ("CNAME", {"value": "target.example.com"}),
    ("TXT", {"value": '"hello"'}),
    ("MX", {"value": "mail.example.com", "priority": 10}),
    ("NS", {"value": "ns1.example.com"}),
    ("PTR", {"value": "host.example.com"}),
    ("SRV", {"value": "sip.example.com", "priority": 10, "weight": 5, "port": 5060}),
    ("CAA", {"value": "letsencrypt.org", "flag": 0, "tag": "issue"}),
])
def test_supported_record_types(client, record_type, payload):
    zone = make_zone(client)
    response = client.post(f"/api/hosted-zones/{zone['id']}/records", json={"name": "example.com", "type": record_type, "ttl": 3600, **payload})
    assert response.status_code == 201


def test_invalid_type_and_ttl_are_rejected(client):
    zone = make_zone(client)
    path = f"/api/hosted-zones/{zone['id']}/records"
    assert client.post(path, json={"name": "example.com", "type": "INVALID", "ttl": 300, "value": "x"}).status_code == 422
    assert client.post(path, json={"name": "example.com", "type": "A", "ttl": 0, "value": "x"}).status_code == 422


@pytest.mark.parametrize("payload", [
    {"type": "A", "value": "999.1.1.1"},
    {"type": "AAAA", "value": "192.0.2.1"},
    {"type": "CNAME", "value": "not a hostname"},
    {"type": "MX", "value": "mail.example.com"},
    {"type": "MX", "value": "not a hostname", "priority": 10},
    {"type": "SRV", "value": "sip.example.com", "priority": 10, "weight": 5},
    {"type": "SRV", "value": "not a hostname", "priority": 10, "weight": 5, "port": 5060},
    {"type": "CAA", "value": "letsencrypt.org", "flag": 0},
])
def test_type_specific_validation(client, payload):
    zone = make_zone(client)
    body = {"name": "example.com", "ttl": 300, **payload}
    assert client.post(f"/api/hosted-zones/{zone['id']}/records", json=body).status_code == 422


def test_record_type_filter_search_pagination_and_filtered_total(client):
    zone = make_zone(client)
    path = f"/api/hosted-zones/{zone['id']}/records"
    for index in range(3):
        assert client.post(path, json={"name": f"www-{index}.example.com", "type": "A", "ttl": 300, "value": f"192.0.2.{index + 1}"}).status_code == 201
    assert client.post(path, json={"name": "www.example.com", "type": "AAAA", "ttl": 300, "value": "2001:db8::1"}).status_code == 201
    assert client.post(path, json={"name": "mail.example.com", "type": "MX", "ttl": 300, "value": "mail.example.com", "priority": 10}).status_code == 201

    all_records = client.get(path).json()
    a_records = client.get(f"{path}?type=A").json()
    assert all_records["total"] == 5
    assert a_records["total"] == 3
    assert {record["type"] for record in a_records["items"]} == {"A"}
    combined = client.get(f"{path}?search=www&type=A&page=1&page_size=2").json()
    assert combined["total"] == 3
    assert combined["total_pages"] == 2
    assert len(combined["items"]) == 2
    assert all(record["type"] == "A" and "www" in record["name"] for record in combined["items"])
    assert client.get(f"{path}?type=INVALID").status_code == 422


def test_unknown_zone_requires_auth_and_delete_cascades(client):
    zone = make_zone(client)
    client.post(f"/api/hosted-zones/{zone['id']}/records", json={"name": "example.com", "type": "TXT", "ttl": 300, "value": '"hello"'})
    assert client.get("/api/hosted-zones/99999/records").status_code == 404
    assert client.delete(f"/api/hosted-zones/{zone['id']}").status_code == 204
    with TestingSessionLocal() as session:
        assert session.execute(__import__('sqlalchemy').text("select count(*) from dns_records")).scalar_one() == 0
    unauthenticated = TestClient(app)
    assert unauthenticated.get(f"/api/hosted-zones/{zone['id']}/records").status_code == 401
