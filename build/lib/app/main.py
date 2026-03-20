from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers.health import router as health_router
from app.api.v1 import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.db.session import close_engine, init_engine
from app.tasks.celery_app import celery_app

try:
    # Prefer async client (redis>=5)
    from redis.asyncio import Redis  # type: ignore
except Exception:  # pragma: no cover
    Redis = object  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    logging.getLogger(__name__).info("Starting %s (env=%s)", settings.app_name, settings.app_env)

    # Init infrastructure (engine, cache client placeholders, etc.)
    init_engine(settings.database_url)

    # Create Redis client lazily; for now it's just a placeholder for Celery/other services.
    redis_client = None
    if Redis is not object:
        from app.core.config import get_redis_url

        redis_url = get_redis_url()
        redis_client = Redis.from_url(redis_url, decode_responses=True)

    app.state.redis = redis_client
    app.state.celery_app = celery_app

    yield

    # Shutdown
    if redis_client is not None:
        await redis_client.close()
    await close_engine()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    # /health (non-versioned)
    app.include_router(health_router)
    # /api/v1/*
    app.include_router(api_v1_router)

    return app


app = create_app()

