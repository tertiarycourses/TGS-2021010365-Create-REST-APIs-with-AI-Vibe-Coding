from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app, db_path


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    path = tmp_path / "test.db"
    monkeypatch.setenv("APP_DATABASE", str(path))
    monkeypatch.setenv("APP_SEED_DEMO", "0")
    init_db(path, seed=True)
    app.dependency_overrides[db_path] = lambda: path
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth():
    return {"X-API-Key": "course-demo-key"}


def product_payload(stock=8):
    return {"sku": "NS-TEST-01", "name": "Course Test Product", "price": "19.90", "stock_quantity": stock}


def test_catalog_crud_and_contract_failures(client):
    invalid = client.post("/api/v1/products", json={"sku": "x", "name": "No", "price": -1}, headers=auth())
    assert invalid.status_code == 422
    created = client.post("/api/v1/products", json=product_payload(), headers=auth())
    assert created.status_code == 201
    product = created.json()
    assert product["sku"] == "NS-TEST-01" and product["stock_quantity"] == 8
    duplicate = client.post("/api/v1/products", json=product_payload(), headers=auth())
    assert duplicate.status_code == 409
    patched = client.patch(f"/api/v1/products/{product['id']}", json={"stock_quantity": 12}, headers=auth())
    assert patched.status_code == 200 and patched.json()["name"] == product["name"]
    missing = client.get("/api/v1/products/99999")
    assert missing.status_code == 404 and missing.json()["error"]["code"] == "not_found"


def test_order_is_atomic_and_updates_dashboard(client):
    product = client.post("/api/v1/products", json=product_payload(stock=5), headers=auth()).json()
    customer = client.post(
        "/api/v1/customers",
        json={"name": "Jamie Tan", "email": "jamie@example.com", "company": "Harbour Design"},
        headers=auth(),
    ).json()
    order = client.post(
        "/api/v1/orders",
        json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 2}]},
        headers=auth(),
    )
    assert order.status_code == 201
    assert order.json()["total"] == "39.80"
    current = client.get(f"/api/v1/products/{product['id']}").json()
    assert current["stock_quantity"] == 3
    conflict = client.post(
        "/api/v1/orders",
        json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 4}]},
        headers=auth(),
    )
    assert conflict.status_code == 409
    assert client.get(f"/api/v1/products/{product['id']}").json()["stock_quantity"] == 3
    summary = client.get("/api/v1/dashboard").json()
    assert summary["orders"] == 1 and summary["revenue"] == "39.80"


def test_writes_require_key_and_openapi_is_versioned(client):
    assert client.post("/api/v1/products", json=product_payload()).status_code == 401
    schema = client.get("/openapi.json").json()
    assert schema["openapi"].startswith("3.1")
    assert "/api/v1/products" in schema["paths"]
    assert "/api/v1/orders" in schema["paths"]
    customers = client.get("/api/v1/customers")
    assert customers.status_code == 200
    assert customers.json()[0]["email"] == "aisha@example.com"
