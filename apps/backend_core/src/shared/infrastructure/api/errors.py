"""Shared HTTP infrastructure for the backend API."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.shared.domain.errors import ApplicationError


def register_error_handlers(app: FastAPI) -> None:
    """Map application errors to JSON responses with a stable error shape."""

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request, exc: ApplicationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message},
        )
