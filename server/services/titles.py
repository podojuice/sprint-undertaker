from dataclasses import dataclass
from datetime import UTC, datetime
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.models.character import Character
from server.models.title import Title, TitleVisibility, UserTitle
from server.models.user import User
from server.title_definitions import LEGACY_TITLE_NAMES, TITLE_DEFINITIONS, TitleDefinition


@dataclass
class AwardedTitles:
    names: list[str]
    notifications: list[str]


def _definition_payload(definition: TitleDefinition) -> dict:
    return {
        "name": definition.name,
        "description": definition.description,
        "type": definition.type,
        "visibility": definition.visibility,
        "condition": definition.rule.encode(),
        "theme_color": definition.theme_color,
        "active_start_at": definition.active_start_at,
        "active_end_at": definition.active_end_at,
    }


async def _get_or_create_title(session: AsyncSession, definition: TitleDefinition) -> Title:
    titles_by_name = {
        title.name: title for title in (await session.execute(select(Title))).scalars().all()
    }

    existing = titles_by_name.get(definition.name)
    if existing is None:
        for legacy_name in LEGACY_TITLE_NAMES.get(definition.name, []):
            existing = titles_by_name.get(legacy_name)
            if existing is not None:
                existing.name = definition.name
                break

    payload = _definition_payload(definition)
    if existing is None:
        existing = Title(**payload)
        session.add(existing)
        return existing

    existing.description = payload["description"]
    existing.type = payload["type"]
    existing.visibility = payload["visibility"]
    existing.condition = payload["condition"]
    existing.theme_color = payload["theme_color"]
    existing.active_start_at = payload["active_start_at"]
    existing.active_end_at = payload["active_end_at"]
    return existing


async def seed_titles(session: AsyncSession) -> None:
    for definition in TITLE_DEFINITIONS:
        await _get_or_create_title(session, definition)
    await session.commit()


def get_title_availability_status(title: Title, now: datetime | None = None) -> str:
    active_now = is_title_active(title, now)
    if active_now and title.active_start_at is None and title.active_end_at is None:
        return "always"
    if active_now:
        return "active"
    current_time = now or datetime.now(UTC)
    if title.active_start_at and current_time < title.active_start_at:
        return "upcoming"
    if title.active_end_at and current_time > title.active_end_at:
        return "expired"
    return "inactive"


def is_title_active(title: Title, now: datetime | None = None) -> bool:
    current_time = now or datetime.now(UTC)
    if title.active_start_at and current_time < title.active_start_at:
        return False
    if title.active_end_at and current_time > title.active_end_at:
        return False
    return True


def title_is_obtainable_now(title: Title, unlocked: bool, now: datetime | None = None) -> bool:
    return not unlocked and is_title_active(title, now)


def title_sort_key(title: Title, earned_at: datetime | None) -> tuple[int, int, int, str]:
    unlocked_rank = 0 if earned_at is not None else 1
    availability_rank = 0 if title_is_obtainable_now(title, earned_at is not None) else 1
    visibility_rank = 0 if title.visibility == TitleVisibility.PUBLIC else 1
    return unlocked_rank, availability_rank, visibility_rank, title.name


def _evaluate_rule(rule: dict, character: Character) -> bool:
    kind = rule.get("kind")
    params = rule.get("params", {})
    if kind == "stat_threshold":
        stat_name = str(params["stat"])
        value = int(params["value"])
        return int(getattr(character, stat_name, 0)) >= value
    if kind == "level_threshold":
        value = int(params["value"])
        return character.level >= value
    if kind == "all_of":
        nested_rules = params.get("rules", [])
        return all(_evaluate_rule(nested_rule, character) for nested_rule in nested_rules)
    return False


def _meets_title_condition(title: Title, character: Character) -> bool:
    try:
        rule = json.loads(title.condition)
    except json.JSONDecodeError:
        return False
    return _evaluate_rule(rule, character)


def build_title_status(title: Title, earned_at: datetime | None) -> tuple[str, str]:
    unlocked = earned_at is not None
    availability_status = get_title_availability_status(title)
    if unlocked:
        return "Unlocked", (
            f"Earned on {earned_at.date().isoformat()}." if earned_at is not None else "Unlocked."
        )
    if title_is_obtainable_now(title, unlocked):
        return "Available", "You can unlock this title right now."
    if availability_status == "upcoming":
        return "Scheduled", "This title is not active yet."
    if availability_status == "expired":
        return "Ended", "This title can no longer be unlocked."
    return "Locked", title.description


async def award_titles(session: AsyncSession, user: User, character: Character) -> AwardedTitles:
    owned_ids = set(
        (
            await session.execute(select(UserTitle.title_id).where(UserTitle.user_id == user.id))
        )
        .scalars()
        .all()
    )
    titles = (await session.execute(select(Title))).scalars().all()

    awarded: list[str] = []
    notifications: list[str] = []

    for title in titles:
        if title.id in owned_ids:
            continue
        if not is_title_active(title):
            continue
        if _meets_title_condition(title, character):
            session.add(UserTitle(user_id=user.id, title_id=title.id))
            awarded.append(title.name)

    if awarded and character.title is None:
        character.title = awarded[0]

    for name in awarded:
        notifications.append(f"Title unlocked: {name}")

    if awarded:
        await session.flush()

    return AwardedTitles(names=awarded, notifications=notifications)
