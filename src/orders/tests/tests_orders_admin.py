from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def mock_get_all_orders():
    return [{"order_id": 1, "user_id": 1, "status": "PENDING", "total_amount": 100}]


def mock_update_order_status(order_id: int, status: str):
    if order_id == 1:
        return {"order_id": 1, "status": status}
    return None


@patch('src.orders.controllers.admin_get_all_orders', mock_get_all_orders)
def test_admin_get_all_orders():
    response = client.get("/admin/orders/")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["order_id"] == 1


@patch('src.orders.controllers.admin_update_order_status', mock_update_order_status)
def test_admin_update_order_status():
    response = client.patch("/admin/orders/1/status", json={"status": "SHIPPED"})
    assert response.status_code == 200
    assert response.json()["status"] == "SHIPPED"
