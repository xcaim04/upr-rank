"""Health check endpoint shared across services."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Return liveness status of the backend service."""
    return {"status": "ok", "service": "upr-rank-backend"}
