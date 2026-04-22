from __future__ import annotations

import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers.health import router as health_router
from app.api.v1 import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.db.session import close_engine, init_engine
from app.tasks.celery_app import celery_app

try:
    # Prefer async client (redis>=5)
    from redis.asyncio import Redis  # type: ignore
except Exception:  # pragma: no cover
    Redis = object  # type: ignore

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Initialise logging first — everything after this is structured.
    configure_logging(
        level=settings.log_level,
        json_output=settings.is_aws,
        environment=settings.app_env.value,
    )

    logger.info(
        "app_starting",
        app_name=settings.app_name,
        environment=settings.app_env.value,
        is_aws=settings.is_aws,
        debug_mode=settings.debug_mode,
        version=settings.version,
    )

    # Init infrastructure (engine, cache client placeholders, etc.)
    init_engine(settings.database_url)
    logger.info("database_engine_initialised")

    # Create Redis client lazily; for now it's just a placeholder for Celery/other services.
    redis_client = None
    if Redis is not object:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
        logger.info("redis_client_created", redis_url=_mask_url(settings.redis_url))

    app.state.redis = redis_client
    app.state.celery_app = celery_app

    logger.info("app_ready", app_name=settings.app_name)

    yield

    # Shutdown
    logger.info("app_shutting_down")
    if redis_client is not None:
        await redis_client.close()
        logger.info("redis_client_closed")
    await close_engine()
    logger.info("database_engine_closed")
    logger.info("app_stopped")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        openapi_url="/openapi.json" if not settings.is_production else None,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Middleware (order matters: first added = outermost) ──────────
    # Request logging must be outermost to capture full request duration.
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ──────────────────────────────────────────
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.warning(
            "app_error",
            error_code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    # /health (non-versioned)
    app.include_router(health_router)
    # /api/v1/*
    app.include_router(api_v1_router)

    return app


def _mask_url(url: str) -> str:
    """Mask password in connection URLs for safe logging."""
    try:
        if "@" in url:
            # scheme://user:pass@host → scheme://***@host
            scheme_rest = url.split("://", 1)
            if len(scheme_rest) == 2:
                creds_host = scheme_rest[1].split("@", 1)
                if len(creds_host) == 2:
                    return f"{scheme_rest[0]}://***@{creds_host[1]}"
    except Exception:
        pass
    return "***"


app = create_app()
