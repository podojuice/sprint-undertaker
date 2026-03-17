from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from server.config import get_settings
from server.database import init_database
from server.api.auth import router as auth_router
from server.api.characters import router as characters_router
from server.api.events import router as events_router
from server.api.installations import router as installations_router
from server.api.notifications import router as notifications_router
from server.api.organizations import router as organizations_router
from server.api.titles import router as titles_router
from server.installers import router as installers_router
from server.web import router as web_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_database(get_settings())
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Sprint Undertaker API", version="0.1.0", lifespan=lifespan)
    static_dir = Path(__file__).parent / "static"

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "environment": settings.env,
        }

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    app.include_router(installers_router)
    app.include_router(web_router)
    app.include_router(auth_router)
    app.include_router(characters_router)
    app.include_router(titles_router)
    app.include_router(installations_router)
    app.include_router(events_router)
    app.include_router(notifications_router)
    app.include_router(organizations_router)

    return app


app = create_app()
