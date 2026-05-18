"""Integration tests against the running Compose stack."""
import os

import pytest
import requests

BASE = os.getenv("GATEWAY_URL", "http://localhost:8088")
TIMEOUT = 10


@pytest.fixture(scope="module")
def client():
    return requests.Session()


def test_frontend_reachable(client):
    r = client.get(BASE, timeout=TIMEOUT)
    assert r.status_code == 200
    assert "SRE Microservices" in r.text


def test_products_list(client):
    r = client.get(f"{BASE}/api/v1/products", timeout=TIMEOUT)
    assert r.status_code == 200
    data = r.json()
    assert "products" in data
    assert len(data["products"]) >= 1


def test_create_order_flow(client):
    r = client.post(
        f"{BASE}/api/v1/orders",
        json={"user_id": "test-user", "product_id": 1, "quantity": 1},
        timeout=TIMEOUT,
    )
    assert r.status_code == 201
    assert r.json().get("status") == "created"


def test_payment_simulation(client):
    r = client.post(
        f"{BASE}/api/v1/payments",
        json={"order_id": 42, "amount": 99.99},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200
    assert r.json().get("status") == "completed"


def test_notification_queue(client):
    r = client.post(
        f"{BASE}/api/v1/notify",
        json={"user_id": "test-user", "message": "pytest"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 202


def test_user_profile(client):
    r = client.get(f"{BASE}/api/v1/users/test-user", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json().get("user_id") == "test-user"


def test_login(client):
    r = client.post(
        f"{BASE}/api/v1/login",
        json={"username": "sre-tester"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 200
    assert "token" in r.json()


def test_orders_list(client):
    r = client.get(f"{BASE}/api/v1/orders", timeout=TIMEOUT)
    assert r.status_code == 200
    assert "orders" in r.json()
