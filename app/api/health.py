# app/api/health.py
# Defines the /health endpoint used to verify the API is running.

from datetime import datetime, timezone
from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return the current health status and timestamp for the API.

    Args:
        None.

    Returns:
        HealthResponse: A payload indicating the service is running and the
            current UTC time in ISO 8601 format.

    Raises:
        None.

    Example:
        GET /health
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )