from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppError(Exception):
    """
    Base application error for consistent API responses.
    """

    message: str
    status_code: int = 500
    code: str = "app_error"


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found", code: str = "not_found"):
        super().__init__(message=message, status_code=404, code=code)

