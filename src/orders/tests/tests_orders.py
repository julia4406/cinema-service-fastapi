from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


@patch('src.orders.controllers.create_order',
       lambda user_id: {"order_id": 1, "status": "PENDING"})
def test_create_order():
    response = client.post("/orders/", json={"user_id": 1})
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"


@patch('src.orders.controllers.get_user_orders',
       lambda user_id: [{"order_id": 1, "status": "PENDING"}])
def test_get_user_orders():
    response = client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["order_id"] == 1


@patch('src.orders.controllers.get_order',
       lambda user_id, order_id: {"order_id": 1, "status": "PENDING"})
def test_get_order():
    response = client.get("/orders/1")
    assert response.status_code == 200
    assert response.json()["order_id"] == 1


@patch('src.orders.controllers.cancel_pending_order',
       lambda user_id, order_id: {"order_id": 1, "status": "CANCELLED"})
def test_cancel_pending_order():
    response = client.patch("/orders/1/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


@patch('src.orders.controllers.confirm_order',
       lambda user_id, order_id: {"order_id": 1, "status": "PAID"})
def test_confirm_order():
    response = client.post("/orders/1/confirm")
    assert response.status_code == 200
    assert response.json()["status"] == "PAID"
