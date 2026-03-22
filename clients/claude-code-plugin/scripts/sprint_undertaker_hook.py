#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


CONFIG_PATH = Path(
    os.environ.get("SPRINT_UNDERTAKER_CLAUDE_CONFIG", "~/.config/sprint-undertaker/claude-code-hook.env")
).expanduser()
STATE_DIR = Path(
    os.environ.get("SPRINT_UNDERTAKER_CLAUDE_STATE_DIR", "~/.config/sprint-undertaker/claude-code-hook-state")
).expanduser()

BATCH_SIZE = 5


def _read_plugin_version() -> str:
    plugin_json = Path(__file__).parent.parent / ".claude-plugin" / "plugin.json"
    try:
        return json.loads(plugin_json.read_text())["version"]
    except Exception:
        return "unknown"


PLUGIN_VERSION = _read_plugin_version()


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


def queue_path() -> Path:
    return STATE_DIR / "queue.json"


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


def enqueue_turn(payload: dict) -> None:
    session_id = session_id_from(payload)
    if not session_id:
        return
    state_path = turn_state_path(session_id)
    turn_state = load_json(state_path)
    if turn_state is None:
        return
    meta = load_json(session_meta_path(session_id)) or {"model_name": "unknown"}

    event = {
        "provider": "claude_code",
        "event_type": "turn_completed",
        "session_id": session_id,
        "occurred_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "metrics": {
            "prompt_count": turn_state["prompt_count"],
            "prompt_length_bucket": turn_state["prompt_length_bucket"],
            "edit_success_count": turn_state["edit_success_count"],
            "validation_success_count": turn_state["validation_success_count"],
            "validation_failure_count": turn_state["validation_failure_count"],
            "tool_failure_count": turn_state["tool_failure_count"],
            "model_name": meta.get("model_name", "unknown"),
        },
        "metadata": {
            "client": "claude_code_hook",
            "installation_name": os.environ.get("SPRINT_UNDERTAKER_INSTALLATION_NAME", "local-claude"),
        },
    }

    path = queue_path()
    queue = []
    if path.exists():
        try:
            queue = json.loads(path.read_text())
        except (json.JSONDecodeError, ValueError):
            queue = []
    queue.append(event)
    path.write_text(json.dumps(queue, separators=(",", ":")) + "\n")
    state_path.unlink(missing_ok=True)

    if len(queue) >= BATCH_SIZE:
        _spawn_flush()


def _spawn_flush() -> None:
    subprocess.Popen(
        [sys.executable, __file__, "--flush"],
        close_fds=True,
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def flush_queue() -> None:
    load_env_file()
    server_url = os.environ.get("SPRINT_UNDERTAKER_SERVER_URL")
    api_key = os.environ.get("SPRINT_UNDERTAKER_API_KEY")
    if not server_url or not api_key:
        return

    path = queue_path()
    if not path.exists():
        return
    try:
        queue = json.loads(path.read_text())
    except (json.JSONDecodeError, ValueError):
        return
    if not queue:
        return

    # clear queue before sending to avoid double-send on retry races
    path.unlink(missing_ok=True)

    from urllib import request as urllib_request

    body = json.dumps({"events": queue}).encode()
    req = urllib_request.Request(
        f"{server_url.rstrip('/')}/api/events/batch",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "X-Plugin-Version": PLUGIN_VERSION,
        },
        method="POST",
    )
    try:
        with urllib_request.urlopen(req, timeout=10) as response:
            response.read()
    except Exception:
        # restore queue on failure so events aren't lost
        path.write_text(json.dumps(queue, separators=(",", ":")) + "\n")


def main() -> int:
    if len(sys.argv) < 2:
        return 0

    if sys.argv[1] == "--flush":
        flush_queue()
        return 0

    load_env_file()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.load(sys.stdin)
    event_name = sys.argv[1]

    if event_name == "SessionStart":
        record_session_meta(payload)
        # flush any leftover events from previous sessions
        if queue_path().exists():
            _spawn_flush()
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
            enqueue_turn(payload)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
