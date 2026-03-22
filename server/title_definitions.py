from dataclasses import dataclass
from datetime import datetime
import json

from server.models.title import TitleType, TitleVisibility


@dataclass(frozen=True)
class TitleRule:
    kind: str
    params: dict[str, int | str]

    def encode(self) -> str:
        return json.dumps({"kind": self.kind, "params": self.params}, separators=(",", ":"))


@dataclass(frozen=True)
class TitleDefinition:
    name: str
    description: str
    type: TitleType
    rule: TitleRule
    theme_color: str
    visibility: TitleVisibility = TitleVisibility.HIDDEN
    active_start_at: datetime | None = None
    active_end_at: datetime | None = None


TITLE_DEFINITIONS: list[TitleDefinition] = [
    TitleDefinition(
        name="Code Berserker",
        description="구현력 10 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.PUBLIC,
        rule=TitleRule(kind="stat_threshold", params={"stat": "impl", "value": 10}),
        theme_color="#d2643f",
    ),
    TitleDefinition(
        name="Reliable Operator",
        description="안정성 10 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.PUBLIC,
        rule=TitleRule(kind="stat_threshold", params={"stat": "stability", "value": 10}),
        theme_color="#2f7a8c",
    ),
    TitleDefinition(
        name="Deep Focus",
        description="집중력 10 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.PUBLIC,
        rule=TitleRule(kind="stat_threshold", params={"stat": "focus", "value": 10}),
        theme_color="#b08a2e",
    ),
    TitleDefinition(
        name="Phantom Maintainer",
        description="안정성과 집중력 모두 3 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(
            kind="all_of",
            params={
                "rules": [
                    {"kind": "stat_threshold", "params": {"stat": "stability", "value": 3}},
                    {"kind": "stat_threshold", "params": {"stat": "focus", "value": 3}},
                ]
            },
        ),
        theme_color="#5f5ba8",
    ),
]


LEVEL_TITLE_DEFINITIONS: list[TitleDefinition] = [
    TitleDefinition(
        name="First Commit Flame",
        description="Lv.2 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(kind="level_threshold", params={"value": 2}),
        theme_color="#e07b39",
    ),
    TitleDefinition(
        name="Reliable Climber",
        description="Lv.5 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(kind="level_threshold", params={"value": 5}),
        theme_color="#5a9e6f",
    ),
    TitleDefinition(
        name="Deep Cycle Operator",
        description="Lv.10 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(kind="level_threshold", params={"value": 10}),
        theme_color="#3a7fbf",
    ),
    TitleDefinition(
        name="Quiet Maintainer",
        description="Lv.15 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(kind="level_threshold", params={"value": 15}),
        theme_color="#7a6fbf",
    ),
    TitleDefinition(
        name="Project Vanguard",
        description="Lv.20 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(kind="level_threshold", params={"value": 20}),
        theme_color="#bf5a5a",
    ),
    TitleDefinition(
        name="Weekly Hunter",
        description="Lv.30 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(kind="level_threshold", params={"value": 30}),
        theme_color="#c47f1a",
    ),
    TitleDefinition(
        name="System Ascendant",
        description="Lv.40 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(kind="level_threshold", params={"value": 40}),
        theme_color="#8f3fbf",
    ),
    TitleDefinition(
        name="Weekly Vanguard",
        description="Lv.50 달성 — 만렙 달성",
        type=TitleType.PERSONAL,
        visibility=TitleVisibility.HIDDEN,
        rule=TitleRule(kind="level_threshold", params={"value": 50}),
        theme_color="#bfa01a",
    ),
]

TITLE_DEFINITIONS = TITLE_DEFINITIONS + LEVEL_TITLE_DEFINITIONS

LEGACY_TITLE_NAMES = {
    "Deep Focus": ["Marathon Builder"],
}
