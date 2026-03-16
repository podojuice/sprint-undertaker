import pytest
from httpx import AsyncClient


async def register_user(client: AsyncClient) -> str:
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "player@example.com",
            "password": "secret123",
            "character_name": "Runner",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


async def create_claude_installation(client: AsyncClient, access_token: str) -> str:
    installation_response = await client.post(
        "/api/installations",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"provider": "claude_code", "installation_name": "local-claude"},
    )
    assert installation_response.status_code == 201
    return installation_response.json()["api_key"]


@pytest.mark.asyncio
async def test_turn_summary_updates_character_progression(client: AsyncClient) -> None:
    access_token = await register_user(client)
    api_key = await create_claude_installation(client, access_token)

    event_response = await client.post(
        "/api/events",
        headers={"X-API-Key": api_key},
        json={
            "provider": "claude_code",
            "event_type": "turn_completed",
            "session_id": "sess-1",
            "occurred_at": "2026-03-15T10:00:00Z",
            "metrics": {
                "prompt_count": 1,
                "prompt_length_bucket": "long",
                "edit_success_count": 2,
                "validation_success_count": 1,
                "validation_failure_count": 0,
                "tool_failure_count": 1,
                "model_name": "claude-sonnet-4-6",
            },
            "metadata": {"client": "claude_code_hook"},
        },
    )
    assert event_response.status_code == 201
    assert event_response.json()["stat_changes"] == {"impl": 2, "focus": 2, "stability": 2}

    character_response = await client.get(
        "/api/characters/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert character_response.status_code == 200
    character = character_response.json()
    assert character["impl"] == 2
    assert character["focus"] == 2
    assert character["stability"] == 2
    assert character["exp"] == 18


@pytest.mark.asyncio
async def test_titles_endpoint_exposes_theme_and_availability(client: AsyncClient) -> None:
    access_token = await register_user(client)
    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = await client.get("/api/titles/me", headers=auth_header)
    assert response.status_code == 200

    titles = response.json()
    assert len(titles) >= 3
    assert titles[0]["theme_color"].startswith("#")
    assert titles[0]["status_label"] in {"Unlocked", "Available", "Scheduled", "Ended", "Locked"}
    assert "status_note" in titles[0]
    assert all(title["name"] != "Marathon Builder" for title in titles)
    assert any(title["name"] == "Deep Focus" for title in titles)


@pytest.mark.asyncio
async def test_activity_endpoint_returns_recent_turn_summaries(client: AsyncClient) -> None:
    access_token = await register_user(client)
    api_key = await create_claude_installation(client, access_token)

    response = await client.post(
        "/api/events",
        headers={"X-API-Key": api_key},
        json={
            "provider": "claude_code",
            "event_type": "turn_completed",
            "session_id": "sess-activity",
            "occurred_at": "2026-03-15T10:00:00Z",
            "metrics": {
                "prompt_count": 1,
                "prompt_length_bucket": "medium",
                "edit_success_count": 1,
                "validation_success_count": 1,
                "validation_failure_count": 0,
                "tool_failure_count": 0,
                "model_name": "claude-sonnet-4-6",
            },
            "metadata": {"client": "claude_code_hook"},
        },
    )
    assert response.status_code == 201

    activity_response = await client.get(
        "/api/characters/me/activity",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert activity_response.status_code == 200
    items = activity_response.json()["items"]
    assert len(items) == 1
    assert items[0]["event_type"] == "turn_completed"
    assert "edit success" in items[0]["summary"]
    assert "impl" in items[0]["stat_hints"]


@pytest.mark.asyncio
async def test_weekly_project_clear_adds_notifications_and_title(client: AsyncClient) -> None:
    access_token = await register_user(client)
    api_key = await create_claude_installation(client, access_token)
    auth_header = {"Authorization": f"Bearer {access_token}"}

    response = await client.post(
        "/api/events",
        headers={"X-API-Key": api_key},
        json={
            "provider": "claude_code",
            "event_type": "turn_completed",
            "session_id": "project-clear",
            "occurred_at": "2026-03-15T10:00:00Z",
            "metrics": {
                "prompt_count": 1,
                "prompt_length_bucket": "long",
                "edit_success_count": 17,
                "validation_success_count": 8,
                "validation_failure_count": 0,
                "tool_failure_count": 0,
                "model_name": "claude-sonnet-4-6",
            },
            "metadata": {"client": "claude_code_hook"},
        },
    )
    assert response.status_code == 201
    notifications = response.json()["notifications"]
    assert any(message.startswith("Project clear!") for message in notifications)
    assert any(message.startswith("Title unlocked: Orbital Breaker") for message in notifications)

    activity_response = await client.get("/api/characters/me/activity", headers=auth_header)
    items = activity_response.json()["items"]
    assert any(item["event_type"] == "project_cleared" for item in items)

    titles_response = await client.get("/api/titles/me", headers=auth_header)
    titles = titles_response.json()
    assert any(title["name"] == "Orbital Breaker" and title["unlocked"] for title in titles)


@pytest.mark.asyncio
async def test_hidden_titles_only_show_after_unlock(client: AsyncClient) -> None:
    access_token = await register_user(client)
    auth_header = {"Authorization": f"Bearer {access_token}"}
    api_key = await create_claude_installation(client, access_token)

    titles_before = (await client.get("/api/titles/me", headers=auth_header)).json()
    assert all(title["name"] != "Phantom Maintainer" for title in titles_before)

    for index in range(3):
        response = await client.post(
            "/api/events",
            headers={"X-API-Key": api_key},
            json={
                "provider": "claude_code",
                "event_type": "turn_completed",
                "session_id": f"sess-{index}",
                "occurred_at": "2026-03-15T10:00:00Z",
                "metrics": {
                    "prompt_count": 1,
                    "prompt_length_bucket": "medium",
                    "edit_success_count": 1,
                    "validation_success_count": 1,
                    "validation_failure_count": 0,
                    "tool_failure_count": 0,
                    "model_name": "claude-sonnet-4-6",
                },
                "metadata": {"client": "claude_code_hook"},
            },
        )
        assert response.status_code == 201

    titles_after = (await client.get("/api/titles/me", headers=auth_header)).json()
    hidden_title = next(title for title in titles_after if title["name"] == "Phantom Maintainer")
    assert hidden_title["unlocked"] is True
    assert hidden_title["status_label"] == "Unlocked"


@pytest.mark.asyncio
async def test_unlocked_titles_are_sorted_first(client: AsyncClient) -> None:
    access_token = await register_user(client)
    auth_header = {"Authorization": f"Bearer {access_token}"}
    api_key = await create_claude_installation(client, access_token)

    for index in range(10):
        response = await client.post(
            "/api/events",
            headers={"X-API-Key": api_key},
            json={
                "provider": "claude_code",
                "event_type": "turn_completed",
                "session_id": f"sort-{index}",
                "occurred_at": "2026-03-15T10:00:00Z",
                "metrics": {
                    "prompt_count": 1,
                    "prompt_length_bucket": "medium",
                    "edit_success_count": 1,
                    "validation_success_count": 1,
                    "validation_failure_count": 0,
                    "tool_failure_count": 0,
                    "model_name": "claude-sonnet-4-6",
                },
                "metadata": {"client": "claude_code_hook"},
            },
        )
        assert response.status_code == 201

    titles = (await client.get("/api/titles/me", headers=auth_header)).json()
    unlocked_prefix = [title["unlocked"] for title in titles[:2]]
    assert unlocked_prefix == [True, True]
