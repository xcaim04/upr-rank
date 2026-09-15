"""FastAPI application factory for the UPR-RANK backend."""

from fastapi import FastAPI

from src.shared.config import settings
from src.shared.infrastructure.api.health import router as health_router


def create_app() -> FastAPI:
    """Build the FastAPI application with all routes registered."""
    application = FastAPI(
        title=settings.app_name,
        description="Backend API for the UPR-RANK online judge.",
        version="0.1.0",
    )

    application.include_router(health_router)

    return application


app = create_app()
