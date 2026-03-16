import pytest
from httpx import AsyncClient


async def register(client: AsyncClient, email: str, character_name: str) -> str:
    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "character_name": character_name,
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_and_list_organization_members(client: AsyncClient) -> None:
    owner_token = await register(client, "owner@example.com", "Owner")
    member_token = await register(client, "member@example.com", "Member")

    create_response = await client.post(
        "/api/organizations",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "IceGuild"},
    )
    assert create_response.status_code == 201
    organization_id = create_response.json()["id"]

    join_response = await client.post(
        f"/api/organizations/{organization_id}/join",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert join_response.status_code == 200

    members_response = await client.get(
        f"/api/organizations/{organization_id}/members",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert members_response.status_code == 200
    assert len(members_response.json()) == 2
