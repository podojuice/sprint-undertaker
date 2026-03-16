import os
from collections.abc import AsyncGenerator

import psycopg
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from server.api.deps import get_db_session
from server.main import create_app
from server.services.projects import seed_weekly_projects
from server.services.titles import seed_titles

TEST_DATABASE_URL = os.getenv(
    "RPG_DATABASE_URL",
    "postgresql+asyncpg://rpg:rpg@localhost:5433/rpg_test",
)


def run_migrations() -> None:
    config = Config("alembic.ini")
    os.environ["RPG_DATABASE_URL"] = TEST_DATABASE_URL
    command.upgrade(config, "head")


def reset_database() -> None:
    sync_database_url = TEST_DATABASE_URL.replace("+asyncpg", "")
    with psycopg.connect(sync_database_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS public CASCADE")
            cur.execute("CREATE SCHEMA public")
            cur.execute("GRANT ALL ON SCHEMA public TO rpg")
            cur.execute("GRANT ALL ON SCHEMA public TO public")


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    reset_database()
    run_migrations()


@pytest.fixture(autouse=True)
def clean_database() -> None:
    tables = [
        "activity_events",
        "provider_installations",
        "characters",
        "user_titles",
        "titles",
        "project_progress",
        "weekly_projects",
        "users",
        "organizations",
    ]
    sync_database_url = TEST_DATABASE_URL.replace("+asyncpg", "")
    with psycopg.connect(sync_database_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
    yield


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine_test,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        await seed_titles(session)
        await seed_weekly_projects(session)

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    await engine_test.dispose()
