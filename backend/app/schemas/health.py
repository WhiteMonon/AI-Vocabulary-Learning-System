"""Health check schema."""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response schema cho health check endpoint."""
    
    status: str
    version: str
    database: str
