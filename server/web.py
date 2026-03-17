import json
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

TEMPLATE_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

router = APIRouter(include_in_schema=False)


PLUGIN_DIR_DEFAULT = "$HOME/.config/sprint-undertaker/plugin"


def build_plugin_dir_snippet() -> str:
    return json.dumps({"pluginDirs": [PLUGIN_DIR_DEFAULT]}, indent=2)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "home.html",
        {"request": request},
    )


@router.get("/install/claude-code", response_class=RedirectResponse)
async def claude_code_install_redirect() -> RedirectResponse:
    return RedirectResponse(url="/setup", status_code=301)


@router.get("/app", response_class=RedirectResponse)
async def app_redirect() -> RedirectResponse:
    return RedirectResponse(url="/character", status_code=301)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"request": request})


@router.get("/character", response_class=HTMLResponse)
async def character_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "character.html", {"request": request})


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "history.html", {"request": request})


@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "setup.html",
        {
            "request": request,
            "plugin_dir_snippet": build_plugin_dir_snippet(),
            "plugin_dir_default": PLUGIN_DIR_DEFAULT,
        },
    )
