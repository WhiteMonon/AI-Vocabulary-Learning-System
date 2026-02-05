"""
Database session management.
Tạo engine và session factory cho SQLModel.
"""
from typing import Generator
from sqlmodel import Session, create_engine
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Tạo database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries trong debug mode
    pool_pre_ping=True,   # Verify connections trước khi sử dụng
    pool_size=5,          # Connection pool size
    max_overflow=10       # Maximum overflow connections
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function để get database session.
    Sử dụng trong FastAPI dependency injection.
    
    Yields:
        Database session
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()
