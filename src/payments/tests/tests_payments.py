from typing import AsyncGenerator, Callable
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session_postgresql import get_postgresql_db
from src.email.email_service import get_email_service
from src.main import app


@pytest.fixture
async def mock_db() -> AsyncGenerator[AsyncMock, None]:
    db = AsyncMock(spec=AsyncSession)
    yield db


@pytest.fixture
async def mock_email_service() -> AsyncGenerator[AsyncMock, None]:
    email_service = AsyncMock()
    yield email_service


@pytest.fixture
async def client(
        mock_db: Callable, mock_email_service: Callable
) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_postgresql_db] = lambda: mock_db
    app.dependency_overrides[get_email_service] = lambda: mock_email_service
    async with AsyncClient(base_url="http://test") as ac:
        yield ac


def test_success_payment(client: TestClient) -> None:
    response = client.get("/api/v1/payments/success")
    assert response.status_code == 200
    assert response.json() == {"message": "The payment has been successfully completed."}


def test_cancel_payment(client: TestClient) -> None:
    response = client.get("/api/v1/payments/cancel")
    assert response.status_code == 200
    assert response.json() == {"message": "The payment has been canceled."}
