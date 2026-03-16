from dataclasses import dataclass

from server.models.character import Character
from server.schemas.event import TurnSummaryMetrics


@dataclass
class ProgressionResult:
    stat_changes: dict[str, int]
    exp_gained: int
    level_up: bool
    notifications: list[str]


def required_exp_for_level(level: int) -> int:
    return int(100 * (level**1.5))


def _focus_delta(metrics: TurnSummaryMetrics) -> int:
    delta = 1 if metrics.prompt_count > 0 else 0
    if metrics.prompt_length_bucket == "long":
        delta += 1
    return delta


def _stability_delta(metrics: TurnSummaryMetrics) -> int:
    delta = metrics.validation_success_count
    recovered_after_failure = metrics.tool_failure_count > 0 and (
        metrics.edit_success_count > 0 or metrics.validation_success_count > 0
    )
    if recovered_after_failure:
        delta += 1
    return delta


def apply_turn_summary(character: Character, metrics: TurnSummaryMetrics) -> ProgressionResult:
    stat_changes = {
        "impl": metrics.edit_success_count,
        "focus": _focus_delta(metrics),
        "stability": _stability_delta(metrics),
    }
    exp_gained = (stat_changes["impl"] * 4) + (stat_changes["stability"] * 3) + (
        stat_changes["focus"] * 2
    )

    for field, change in stat_changes.items():
        setattr(character, field, getattr(character, field) + change)

    character.exp += exp_gained

    notifications: list[str] = []
    previous_level = character.level
    while character.exp >= required_exp_for_level(character.level):
        character.level += 1

    level_up = character.level > previous_level
    if level_up:
        notifications.append(f"레벨 업! Lv.{previous_level} -> Lv.{character.level}")

    filtered_changes = {key: value for key, value in stat_changes.items() if value > 0}
    return ProgressionResult(
        stat_changes=filtered_changes,
        exp_gained=exp_gained,
        level_up=level_up,
        notifications=notifications,
    )
