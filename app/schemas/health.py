# app/schemas/health.py
# Pydantic model defining the response shape for the /health endpoint.

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema returned by GET /health."""

    status: str
    timestamp: str