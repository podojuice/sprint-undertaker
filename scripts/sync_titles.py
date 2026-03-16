#!/usr/bin/env python3

import asyncio
import os

from server.database import create_session_factory
from server.services.titles import seed_titles


async def main() -> None:
    database_url = os.environ.get("RPG_DATABASE_URL")
    if not database_url:
        raise SystemExit("RPG_DATABASE_URL is required")
    engine, session_factory = create_session_factory(database_url)
    try:
        async with session_factory() as session:
            await seed_titles(session)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
