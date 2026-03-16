#!/usr/bin/env python3

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import request


CONFIG_PATH = Path(
    os.environ.get("IDLE_RPG_CLAUDE_CONFIG", "~/.config/idle-rpg/claude-code-hook.env")
).expanduser()


def load_env_file() -> None:
    if not CONFIG_PATH.exists():
        return
    for raw_line in CONFIG_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def exp_bar(exp: int, exp_to_next: int, width: int = 20) -> str:
    total = exp + exp_to_next
    filled = int(width * exp / total) if total > 0 else 0
    return "█" * filled + "░" * (width - filled)


def main() -> int:
    load_env_file()
    server_url = os.environ.get("IDLE_RPG_SERVER_URL")
    api_key = os.environ.get("IDLE_RPG_API_KEY")

    if not server_url or not api_key:
        print(f"Error: IDLE_RPG_SERVER_URL and IDLE_RPG_API_KEY must be set in {CONFIG_PATH}")
        return 1

    req = request.Request(
        f"{server_url.rstrip('/')}/api/characters/status",
        headers={"X-Api-Key": api_key},
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    name = data["name"]
    char_class = data["character_class"]
    level = data["level"]
    exp = data["exp"]
    exp_to_next = data["exp_to_next_level"]
    title = data.get("title") or "(no title)"
    impl = data["impl"]
    stability = data["stability"]
    focus = data["focus"]

    bar = exp_bar(exp, exp_to_next)

    print()
    print(f"  {name}  [{title}]")
    print(f"  {char_class}  Lv.{level}")
    print(f"  EXP [{bar}] {exp} / {exp + exp_to_next}")
    print()
    print(f"  impl      {impl:>5}")
    print(f"  stability {stability:>5}")
    print(f"  focus     {focus:>5}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
