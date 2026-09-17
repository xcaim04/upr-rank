"""FastAPI application factory for the UPR-RANK backend."""

from fastapi import FastAPI

from src.auth.infrastructure.api.routes import router as auth_router
from src.shared.config import settings
from src.shared.infrastructure.api.errors import register_error_handlers
from src.shared.infrastructure.api.health import router as health_router
from src.user.infrastructure.api.routes import router as user_router


def create_app() -> FastAPI:
    """Build the FastAPI application with all routes registered."""
    application = FastAPI(
        title=settings.app_name,
        description="Backend API for the UPR-RANK online judge.",
        version="0.1.0",
    )

    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(user_router)

    register_error_handlers(application)

    return application


app = create_app()
