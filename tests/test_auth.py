import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient) -> None:
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "secret123",
            "character_name": "IceHero",
        },
    )

    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["email"] == "test@example.com"
    assert register_data["access_token"]

    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["email"] == "test@example.com"
