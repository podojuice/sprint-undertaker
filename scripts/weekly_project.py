#!/usr/bin/env python3
"""Weekly project management script.

Usage:
  # Create a new project
  uv run scripts/weekly_project.py create \
    --slug "launch-the-orbital-stack" \
    --title "Launch the Orbital Stack" \
    --theme space \
    --description "Push the orbital stack over the line before the weekly window closes." \
    --target 100 \
    --clear-title "Orbital Breaker" \
    --starts "2026-03-24 00:00" \
    --ends "2026-03-30 23:59"

  # List all projects
  uv run scripts/weekly_project.py list
"""

from __future__ import annotations

import argparse
import asyncio
import os
from datetime import UTC, datetime

from dotenv import load_dotenv
from sqlalchemy import select

from server.database import create_session_factory
from server.models.weekly_project import WeeklyProject


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)


async def cmd_create(args: argparse.Namespace, session_factory) -> None:
    async with session_factory() as session:
        existing = (
            await session.execute(select(WeeklyProject).where(WeeklyProject.slug == args.slug))
        ).scalar_one_or_none()
        if existing is not None:
            raise SystemExit(f"Error: slug '{args.slug}' already exists (id={existing.id})")

        project = WeeklyProject(
            slug=args.slug,
            title=args.title,
            theme=args.theme,
            description=args.description,
            target_progress=args.target,
            clear_title_name=args.clear_title,
            starts_at=parse_dt(args.starts),
            ends_at=parse_dt(args.ends),
            active=True,
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)

    print(f"Created: [{project.id}] {project.title}")
    print(f"  slug        : {project.slug}")
    print(f"  theme       : {project.theme}")
    print(f"  target      : {project.target_progress}")
    print(f"  clear title : {project.clear_title_name}")
    print(f"  starts_at   : {project.starts_at.isoformat()}")
    print(f"  ends_at     : {project.ends_at.isoformat()}")


async def cmd_list(session_factory) -> None:
    async with session_factory() as session:
        projects = (
            await session.execute(select(WeeklyProject).order_by(WeeklyProject.starts_at))
        ).scalars().all()

    if not projects:
        print("No projects found.")
        return

    now = datetime.now(UTC)
    for p in projects:
        if not p.active:
            status = "inactive"
        elif p.ends_at < now:
            status = "expired"
        elif p.starts_at > now:
            status = "upcoming"
        else:
            status = "ACTIVE"
        print(f"[{p.id}] {p.title}  ({status})")
        print(f"       {p.starts_at.strftime('%Y-%m-%d')} ~ {p.ends_at.strftime('%Y-%m-%d')}  target={p.target_progress}  clear_title={p.clear_title_name}")


async def main() -> None:
    load_dotenv()
    database_url = os.environ.get("RPG_DATABASE_URL")
    if not database_url:
        raise SystemExit("RPG_DATABASE_URL is required")

    parser = argparse.ArgumentParser(description="Weekly project management")
    sub = parser.add_subparsers(dest="command", required=True)

    create_p = sub.add_parser("create", help="Create a new weekly project")
    create_p.add_argument("--slug", required=True)
    create_p.add_argument("--title", required=True)
    create_p.add_argument("--theme", required=True)
    create_p.add_argument("--description", required=True)
    create_p.add_argument("--target", type=int, default=100)
    create_p.add_argument("--clear-title", required=True)
    create_p.add_argument("--starts", required=True, help="YYYY-MM-DD HH:MM (UTC)")
    create_p.add_argument("--ends", required=True, help="YYYY-MM-DD HH:MM (UTC)")

    sub.add_parser("list", help="List all weekly projects")

    args = parser.parse_args()

    engine, session_factory = create_session_factory(database_url)
    try:
        if args.command == "create":
            await cmd_create(args, session_factory)
        elif args.command == "list":
            await cmd_list(session_factory)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
