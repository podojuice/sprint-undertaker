from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse

PLUGIN_DIR = Path(__file__).resolve().parent.parent / "clients" / "claude-code-plugin"

router = APIRouter(include_in_schema=False)


def _read_plugin_file(relative: str) -> str:
    return (PLUGIN_DIR / relative).read_text()


@router.get("/install/claude-code.sh", response_class=PlainTextResponse)
async def claude_code_installer_script(
    request: Request,
    api_key: str | None = Query(default=None),
    installation_name: str = Query(default="local-claude"),
) -> PlainTextResponse:
    server_url = str(request.base_url).rstrip("/")
    api_key_value = api_key or "rpg_sk_replace_me"

    plugin_json = _read_plugin_file(".claude-plugin/plugin.json")
    hooks_json = _read_plugin_file("hooks/hooks.json")
    hook_script = _read_plugin_file("scripts/idle_rpg_claude_hook.py")
    rpg_status_script = _read_plugin_file("scripts/rpg_status.py")
    skill_md = _read_plugin_file("skills/rpg-status/SKILL.md")

    script = f"""#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${{IDLE_RPG_CONFIG_DIR:-$HOME/.config/idle-rpg}}"
PLUGIN_DIR="$CONFIG_DIR/plugin"
CONFIG_PATH="$CONFIG_DIR/claude-code-hook.env"
SERVER_URL="{server_url}"
API_KEY_VALUE="{api_key_value}"
INSTALLATION_NAME_VALUE="{installation_name}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to run the Idle RPG plugin." >&2
  echo "Install Python 3 first, then rerun this installer." >&2
  exit 1
fi

mkdir -p "$PLUGIN_DIR/.claude-plugin"
mkdir -p "$PLUGIN_DIR/hooks"
mkdir -p "$PLUGIN_DIR/scripts"
mkdir -p "$PLUGIN_DIR/skills/rpg-status"

cat > "$CONFIG_PATH" <<EOF_CONFIG
IDLE_RPG_SERVER_URL=$SERVER_URL
IDLE_RPG_API_KEY=$API_KEY_VALUE
IDLE_RPG_INSTALLATION_NAME=$INSTALLATION_NAME_VALUE
EOF_CONFIG

cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" <<'EOF_PLUGIN_JSON'
{plugin_json}
EOF_PLUGIN_JSON

cat > "$PLUGIN_DIR/hooks/hooks.json" <<'EOF_HOOKS'
{hooks_json}
EOF_HOOKS

cat > "$PLUGIN_DIR/scripts/idle_rpg_claude_hook.py" <<'EOF_HOOK'
{hook_script}
EOF_HOOK
chmod +x "$PLUGIN_DIR/scripts/idle_rpg_claude_hook.py"

cat > "$PLUGIN_DIR/scripts/rpg_status.py" <<'EOF_STATUS'
{rpg_status_script}
EOF_STATUS
chmod +x "$PLUGIN_DIR/scripts/rpg_status.py"

cat > "$PLUGIN_DIR/skills/rpg-status/SKILL.md" <<'EOF_SKILL'
{skill_md}
EOF_SKILL

cat <<EOF_DONE
Idle RPG plugin installed.

Plugin directory:
  $PLUGIN_DIR

Config file:
  $CONFIG_PATH

Next step:
  Start Claude Code with the plugin:
    claude --plugin-dir "$PLUGIN_DIR"

  Or add it permanently to your project's .claude/settings.local.json:
    {{"pluginDirs": ["$PLUGIN_DIR"]}}
EOF_DONE
"""
    return PlainTextResponse(script)
