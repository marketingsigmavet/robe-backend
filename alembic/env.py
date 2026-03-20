from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _get_database_url() -> str:
    # Import here so Alembic env loading doesn't require app code at import-time.
    from app.core.config import get_settings

    return get_settings().database_url


def _to_sync_url(database_url: str) -> str:
    # Prefer sync driver for Alembic (more reliable autogenerate path).
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    return database_url


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

    database_url = _to_sync_url(_get_database_url())

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
    Run migrations with an active DB connection.
    """

    database_url = _to_sync_url(_get_database_url())
    connectable = create_engine(database_url, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

