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
    visibility: TitleVisibility
    rule: TitleRule
    theme_color: str
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


LEGACY_TITLE_NAMES = {
    "Deep Focus": ["Marathon Builder"],
}
