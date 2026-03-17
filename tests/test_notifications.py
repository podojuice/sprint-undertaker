import pytest
from httpx import AsyncClient


async def setup_user_and_installation(client: AsyncClient) -> tuple[str, str]:
    response = await client.post(
        "/api/auth/register",
        json={"email": "notif@example.com", "password": "secret123", "character_name": "Ranger"},
    )
    assert response.status_code == 201
    access_token = response.json()["access_token"]

    installation_response = await client.post(
        "/api/installations",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"provider": "claude_code", "installation_name": "local"},
    )
    assert installation_response.status_code == 201
    api_key = installation_response.json()["api_key"]

    return access_token, api_key


async def send_turn(client: AsyncClient, api_key: str, **metric_overrides: int | str) -> dict:
    metrics = {
        "prompt_count": 1,
        "prompt_length_bucket": "medium",
        "edit_success_count": 1,
        "validation_success_count": 0,
        "validation_failure_count": 0,
        "tool_failure_count": 0,
        "model_name": "claude-sonnet-4-6",
        **metric_overrides,
    }
    response = await client.post(
        "/api/events",
        headers={"X-API-Key": api_key},
        json={
            "provider": "claude_code",
            "event_type": "turn_completed",
            "session_id": "sess-notif",
            "occurred_at": "2026-03-17T10:00:00Z",
            "metrics": metrics,
            "metadata": {},
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_no_notifications_initially(client: AsyncClient) -> None:
    _, api_key = await setup_user_and_installation(client)

    response = await client.get("/api/notifications/me", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_level_up_creates_notification(client: AsyncClient) -> None:
    _, api_key = await setup_user_and_installation(client)

    # enough edits to level up (need 100 exp, impl*4 = 4 per turn, need ~25 turns, or bulk)
    await send_turn(client, api_key, edit_success_count=25)

    response = await client.get("/api/notifications/me", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] > 0
    categories = [item["category"] for item in data["items"]]
    assert "level_up" in categories
    messages = [item["message"] for item in data["items"]]
    assert any("레벨 업" in msg for msg in messages)


@pytest.mark.asyncio
async def test_mark_read_clears_notifications(client: AsyncClient) -> None:
    _, api_key = await setup_user_and_installation(client)

    await send_turn(client, api_key, edit_success_count=25)

    before = await client.get("/api/notifications/me", headers={"X-API-Key": api_key})
    assert before.json()["unread_count"] > 0

    read_response = await client.post(
        "/api/notifications/me/read", headers={"X-API-Key": api_key}
    )
    assert read_response.status_code == 204

    after = await client.get("/api/notifications/me", headers={"X-API-Key": api_key})
    assert after.json()["unread_count"] == 0
    assert after.json()["items"] == []


@pytest.mark.asyncio
async def test_title_unlock_creates_notification(client: AsyncClient) -> None:
    _, api_key = await setup_user_and_installation(client)

    for i in range(3):
        await send_turn(
            client,
            api_key,
            edit_success_count=1,
            validation_success_count=1,
        )

    response = await client.get("/api/notifications/me", headers={"X-API-Key": api_key})
    data = response.json()
    categories = [item["category"] for item in data["items"]]
    assert "title_unlock" in categories


@pytest.mark.asyncio
async def test_notifications_accumulate_across_turns(client: AsyncClient) -> None:
    _, api_key = await setup_user_and_installation(client)

    # two separate level-up-triggering turns (50 edits = 202 exp each, enough to level up twice)
    await send_turn(client, api_key, edit_success_count=50)
    await client.post("/api/notifications/me/read", headers={"X-API-Key": api_key})
    await send_turn(client, api_key, edit_success_count=50)

    response = await client.get("/api/notifications/me", headers={"X-API-Key": api_key})
    assert response.json()["unread_count"] > 0
