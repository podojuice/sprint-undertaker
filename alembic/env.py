from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from server.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    database_url = context.get_x_argument(as_dictionary=True).get("database_url")
    if database_url:
        return database_url

    import os

    return os.getenv(
        "RPG_DATABASE_URL",
        config.get_main_option("sqlalchemy.url"),
    )


def to_sync_url(database_url: str) -> str:
    return database_url.replace("+asyncpg", "+psycopg")


def run_migrations_offline() -> None:
    url = to_sync_url(get_url())
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = to_sync_url(get_url())
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
