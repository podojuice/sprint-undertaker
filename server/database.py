from collections.abc import AsyncGenerator

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from server.config import Settings, get_settings
from server.services.projects import seed_weekly_projects
from server.services.titles import seed_titles

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def create_session_factory(database_url: str) -> tuple:
    db_engine = create_async_engine(database_url, echo=False, pool_pre_ping=True)
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return db_engine, session_factory


async def seed_database(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as session:
        await seed_titles(session)
        await seed_weekly_projects(session)


async def init_database(app_settings: Settings | None = None) -> None:
    active_settings = app_settings or get_settings()
    db_engine, session_factory = create_session_factory(active_settings.database_url)
    async with db_engine.begin() as conn:
        has_titles_table = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table("titles")
        )
        has_weekly_projects_table = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table("weekly_projects")
        )

    if has_titles_table or has_weekly_projects_table:
        await seed_database(session_factory)

    await db_engine.dispose()
