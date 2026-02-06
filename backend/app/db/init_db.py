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
    Ghi chú: Tables nên được quản lý bởi Alembic migration thay vì create_all.
    """
    logger.info("Skipping database creation via SQLModel (managed by Alembic)")
    # SQLModel.metadata.create_all(engine)


def drop_db() -> None:
    """
    Drop tất cả database tables.
    CẢNH BÁO: Chỉ sử dụng trong development/testing!
    """
    logger.warning("Dropping all database tables...")
    SQLModel.metadata.drop_all(engine)
    logger.warning("All database tables dropped")
