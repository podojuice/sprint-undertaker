import json
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from server.database import SessionLocal
from server.models.character import Character
from server.models.title import Title, TitleVisibility, UserTitle
from server.services.progression import required_exp_for_level

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


@router.get("/u/{nickname}", response_class=HTMLResponse)
async def public_profile(request: Request, nickname: str) -> HTMLResponse:
    async with SessionLocal() as db:
        character = (
            await db.execute(
                select(Character).where(
                    Character.name == nickname,
                    Character.is_public.is_(True),
                )
            )
        ).scalar_one_or_none()

        if character is None:
            return templates.TemplateResponse(
                request, "profile.html", {"request": request, "profile": None, "nickname": nickname},
                status_code=404,
            )

        titles = (
            await db.execute(
                select(Title.name)
                .join(UserTitle, UserTitle.title_id == Title.id)
                .where(
                    UserTitle.user_id == character.user_id,
                    Title.visibility == TitleVisibility.PUBLIC,
                )
                .order_by(UserTitle.earned_at)
            )
        ).scalars().all()

        exp_to_next = max(0, required_exp_for_level(character.level) - character.exp)
        exp_total = character.exp + exp_to_next
        exp_pct = round(character.exp / exp_total * 100) if exp_total > 0 else 0

        return templates.TemplateResponse(
            request,
            "profile.html",
            {
                "request": request,
                "profile": {
                    "name": character.name,
                    "character_class": character.character_class,
                    "level": character.level,
                    "exp": character.exp,
                    "exp_to_next": exp_to_next,
                    "exp_pct": exp_pct,
                    "impl": character.impl,
                    "focus": character.focus,
                    "stability": character.stability,
                    "title": character.title,
                    "titles": list(titles),
                },
                "nickname": nickname,
            },
        )


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
