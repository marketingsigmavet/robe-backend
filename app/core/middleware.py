"""
HTTP request / response logging middleware.

Automatically logs every request with:
- ``request_id`` – unique per request (also set in ``X-Request-ID`` header)
- ``method`` / ``path`` / ``status_code`` / ``duration_ms``
- Client IP address

The ``request_id`` is bound via structlog's ``contextvars`` so any log
emitted *during* the request will also include it.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger("app.middleware.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every HTTP request and response.

    Binds ``request_id`` into structlog's contextvars so all downstream
    log calls within the same request automatically include it.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # ── Generate or accept a request ID ────────────────────────────
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]

        # Bind context for this request (auto-cleared when the context exits)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
        )

        # ── Capture request metadata ──────────────────────────────────
        client_ip = _get_client_ip(request)
        method = request.method
        path = request.url.path
        query = str(request.url.query) if request.url.query else None

        log_data: dict[str, Any] = {
            "method": method,
            "path": path,
            "client_ip": client_ip,
        }
        if query:
            log_data["query"] = query

        logger.info("request_started", **log_data)

        # ── Process request ────────────────────────────────────────────
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "request_failed",
                **log_data,
                duration_ms=duration_ms,
                exc_info=True,
            )
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # ── Log the response ──────────────────────────────────────────
        status_code = response.status_code

        log_fn = logger.info
        if status_code >= 500:
            log_fn = logger.error
        elif status_code >= 400:
            log_fn = logger.warning

        log_fn(
            "request_completed",
            **log_data,
            status_code=status_code,
            duration_ms=duration_ms,
        )

        # ── Set the request-ID header on the response ─────────────────
        response.headers["X-Request-ID"] = request_id
        return response


def _get_client_ip(request: Request) -> str:
    """
    Extract the real client IP, respecting proxy headers.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can be "client, proxy1, proxy2"
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
