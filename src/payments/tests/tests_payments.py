import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from src.main import app
from src.database.session_postgresql import get_postgresql_db
from src.email.email_service import get_email_service


@pytest.fixture
async def mock_db():
    db = AsyncMock(spec=AsyncSession)
    yield db


@pytest.fixture
async def mock_email_service():
    email_service = AsyncMock()
    yield email_service


@pytest.fixture
async def client(mock_db, mock_email_service):
    app.dependency_overrides[get_postgresql_db] = lambda: mock_db
    app.dependency_overrides[get_email_service] = lambda: mock_email_service
    async with AsyncClient(base_url="http://test") as ac:
        yield ac


def test_success_payment(client: TestClient):
    response = client.get("/api/v1/payments/success")
    assert response.status_code == 200
    assert response.json() == {"message": "The payment has been successfully completed."}


def test_cancel_payment(client: TestClient):
    response = client.get("/api/v1/payments/cancel")
    assert response.status_code == 200
    assert response.json() == {"message": "The payment has been canceled."}
