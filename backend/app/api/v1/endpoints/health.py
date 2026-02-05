"""
Health check endpoint.
Kiểm tra trạng thái của application và database connection.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.api.deps import get_db
from app.schemas.health import HealthResponse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Health check endpoint.
    
    Kiểm tra:
    - Application status
    - Database connection
    
    Returns:
        HealthResponse với status, version, và database status
    """
    try:
        # Test database connection
        db.exec(select(1))
        db_status = "connected"
        logger.debug("Health check: database connection OK")
    except Exception as e:
        logger.error(f"Health check: database connection failed - {e}")
        db_status = "disconnected"
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        database=db_status
    )
