#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request


CONFIG_PATH = Path(
    os.environ.get("SPRINT_UNDERTAKER_CLAUDE_CONFIG", "~/.config/sprint-undertaker/claude-code-hook.env")
).expanduser()
STATE_DIR = Path(
    os.environ.get("SPRINT_UNDERTAKER_CLAUDE_STATE_DIR", "~/.config/sprint-undertaker/claude-code-hook-state")
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


def session_id_from(payload: dict) -> str | None:
    return payload.get("session_id") or payload.get("sessionId")


def session_meta_path(session_id: str) -> Path:
    return STATE_DIR / f"{session_id}.meta.json"


def turn_state_path(session_id: str) -> Path:
    return STATE_DIR / f"{session_id}.turn.json"


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, separators=(",", ":")) + "\n")


def prompt_length_bucket(prompt: str) -> str:
    length = len(prompt)
    if length < 80:
        return "short"
    if length < 240:
        return "medium"
    return "long"


_RUNNER_PREFIXES = {"uv", "npx", "bunx", "pnpx", "pipx"}


def classify_bash(command: str) -> str:
    try:
        parts = shlex.split(command)
    except ValueError:
        return "unknown"
    if not parts:
        return "unknown"
    # Strip runner prefixes: "uv run pytest ..." → "pytest ..."
    if parts[0] in _RUNNER_PREFIXES and len(parts) > 2 and parts[1] == "run":
        parts = parts[2:]
    joined = " ".join(parts[:3])
    if joined.startswith(("pytest", "npm test", "pnpm test", "yarn test", "go test", "cargo test")):
        return "test"
    if joined.startswith(("ruff check", "eslint", "tsc", "mypy", "cargo clippy")):
        return "lint"
    return "other"


def init_turn(payload: dict) -> None:
    session_id = session_id_from(payload)
    if not session_id:
        return
    prompt = payload.get("prompt", "")
    turn_state = {
        "session_id": session_id,
        "prompt_count": 1,
        "prompt_length_bucket": prompt_length_bucket(prompt),
        "edit_success_count": 0,
        "validation_success_count": 0,
        "validation_failure_count": 0,
        "tool_failure_count": 0,
    }
    write_json(turn_state_path(session_id), turn_state)


def update_turn(payload: dict, success: bool) -> None:
    session_id = session_id_from(payload)
    if not session_id:
        return
    state_path = turn_state_path(session_id)
    turn_state = load_json(state_path)
    if turn_state is None:
        return
    tool_name = payload.get("tool_name")
    if success and tool_name in {"Edit", "MultiEdit"}:
        turn_state["edit_success_count"] += 1
    if tool_name == "Bash":
        category = classify_bash((payload.get("tool_input") or {}).get("command", ""))
        if category in {"test", "lint"}:
            if success:
                turn_state["validation_success_count"] += 1
            else:
                turn_state["validation_failure_count"] += 1
    if not success:
        turn_state["tool_failure_count"] += 1
    write_json(state_path, turn_state)


def record_session_meta(payload: dict) -> None:
    session_id = session_id_from(payload)
    if not session_id:
        return
    write_json(
        session_meta_path(session_id),
        {"model_name": payload.get("model", "unknown")},
    )


def post_turn_summary(payload: dict) -> None:
    session_id = session_id_from(payload)
    if not session_id:
        return
    state_path = turn_state_path(session_id)
    turn_state = load_json(state_path)
    if turn_state is None:
        return
    meta = load_json(session_meta_path(session_id)) or {"model_name": "unknown"}
    metrics = {
        "prompt_count": turn_state["prompt_count"],
        "prompt_length_bucket": turn_state["prompt_length_bucket"],
        "edit_success_count": turn_state["edit_success_count"],
        "validation_success_count": turn_state["validation_success_count"],
        "validation_failure_count": turn_state["validation_failure_count"],
        "tool_failure_count": turn_state["tool_failure_count"],
        "model_name": meta.get("model_name", "unknown"),
    }
    server_url = os.environ.get("SPRINT_UNDERTAKER_SERVER_URL")
    api_key = os.environ.get("SPRINT_UNDERTAKER_API_KEY")
    if not server_url or not api_key:
        return
    body = json.dumps(
        {
            "provider": "claude_code",
            "event_type": "turn_completed",
            "session_id": session_id,
            "occurred_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "metrics": metrics,
            "metadata": {
                "client": "claude_code_hook",
                "installation_name": os.environ.get("SPRINT_UNDERTAKER_INSTALLATION_NAME", "local-claude"),
            },
        }
    ).encode()
    req = request.Request(
        f"{server_url.rstrip('/')}/api/events",
        data=body,
        headers={"Content-Type": "application/json", "X-API-Key": api_key},
        method="POST",
    )
    with request.urlopen(req, timeout=3) as response:
        response_body = response.read().decode()
        if response_body:
            try:
                response_json = json.loads(response_body)
            except json.JSONDecodeError:
                response_json = {}
            pass
    state_path.unlink(missing_ok=True)


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    load_env_file()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.load(sys.stdin)
    event_name = sys.argv[1]

    if event_name == "SessionStart":
        record_session_meta(payload)
        return 0
    if event_name == "UserPromptSubmit":
        init_turn(payload)
        return 0
    if event_name == "PostToolUse":
        update_turn(payload, success=True)
        return 0
    if event_name == "PostToolUseFailure":
        update_turn(payload, success=False)
        return 0
    if event_name == "Stop":
        try:
            post_turn_summary(payload)
        except Exception:
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
