"""
Database initialization utilities.
"""
from sqlmodel import SQLModel
from app.db.session import engine
from app.core.logging import get_logger

logger = get_logger(__name__)


def init_db() -> None:
    """
    Initialize database.
    Tạo tất cả tables từ SQLModel metadata.
    """
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def drop_db() -> None:
    """
    Drop tất cả database tables.
    CẢNH BÁO: Chỉ sử dụng trong development/testing!
    """
    logger.warning("Dropping all database tables...")
    SQLModel.metadata.drop_all(engine)
    logger.warning("All database tables dropped")
