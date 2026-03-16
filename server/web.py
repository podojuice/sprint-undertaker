import json
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

TEMPLATE_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

router = APIRouter(include_in_schema=False)


def build_claude_hook_snippet() -> str:
    return json.dumps(
        {
            "hooks": {
                "SessionStart": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" SessionStart',
                            }
                        ]
                    }
                ],
                "UserPromptSubmit": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" UserPromptSubmit',
                            }
                        ]
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": "Edit|MultiEdit|Bash",
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" PostToolUse',
                            }
                        ],
                    }
                ],
                "PostToolUseFailure": [
                    {
                        "matcher": "Edit|MultiEdit|Bash",
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" PostToolUseFailure',
                            }
                        ],
                    }
                ],
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" Stop',
                            }
                        ]
                    }
                ],
            }
        },
        indent=2,
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "home.html",
        {"request": request},
    )


@router.get("/install/claude-code", response_class=HTMLResponse)
async def claude_code_install(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "install_claude_code.html",
        {
            "request": request,
            "install_command": f'curl -fsSL "{request.base_url}install/claude-code.sh" | bash',
            "hook_snippet": build_claude_hook_snippet(),
        },
    )


@router.get("/app", response_class=HTMLResponse)
async def app_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "app.html",
        {"request": request},
    )
