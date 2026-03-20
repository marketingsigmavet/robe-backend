from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _get_database_url() -> str:
    # Import here so Alembic env loading doesn't require app code at import-time.
    from app.core.config import get_settings

    return get_settings().database_url


def _get_target_metadata():
    # Ensure models are imported so Base.metadata is populated.
    import app.models  # noqa: F401

    from app.db.base import Base

    return Base.metadata


target_metadata = _get_target_metadata()


def run_migrations_offline() -> None:
    """
    Run migrations without an active DB connection.
    """

    # Use the same configured URL (asyncpg dialect is installed for offline rendering too).
    database_url = _get_database_url()

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations with an active DB connection (async SQLAlchemy).
    """

    database_url = _get_database_url()
    connectable: AsyncEngine = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    async def _run() -> None:
        async with connectable.connect() as connection:

            def do_run_migrations(sync_connection) -> None:
                context.configure(
                    connection=sync_connection,
                    target_metadata=target_metadata,
                    compare_type=True,
                )

                with context.begin_transaction():
                    context.run_migrations()

            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    asyncio.run(_run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

