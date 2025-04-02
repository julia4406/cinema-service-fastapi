import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_cart(async_client: AsyncClient):
    response = await async_client.get("/cart/")
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_create_cart(async_client: AsyncClient):
    response = await async_client.post("/cart/")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_add_item_to_cart(async_client: AsyncClient):
    movie_id = 1
    response = await async_client.post(f"/cart/items/{movie_id}")
    assert response.status_code == status.HTTP_201_CREATED
    assert "movie_id" in response.json()


@pytest.mark.asyncio
async def test_remove_item_from_cart(async_client: AsyncClient):
    item_id = 1
    response = await async_client.delete(f"/cart/items/{item_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Item removed successfully"


@pytest.mark.asyncio
async def test_clear_cart(async_client: AsyncClient):
    response = await async_client.delete("/cart/clear/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Cart cleared successfully"


@pytest.mark.asyncio
async def test_admin_get_user_cart(async_client: AsyncClient):
    user_id = 1
    response = await async_client.get(f"/admin/{user_id}/cart")
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_admin_add_movie_to_cart(async_client: AsyncClient):
    user_id, movie_id = 1, 2
    response = await async_client.post(f"/admin/{user_id}/cart/items/{movie_id}")
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_admin_remove_movie_from_cart(async_client: AsyncClient):
    user_id, movie_id = 1, 2
    response = await async_client.delete(f"/admin/{user_id}/cart/items/{movie_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Item removed successfully"


@pytest.mark.asyncio
async def test_admin_clear_user_cart(async_client: AsyncClient):
    user_id = 1
    response = await async_client.delete(f"/admin/{user_id}/cart")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Cart cleared successfully"
