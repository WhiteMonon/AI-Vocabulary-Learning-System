"""
Dependency injection functions.
Cung cấp common dependencies cho FastAPI endpoints.
"""
from typing import Generator
from sqlmodel import Session
from app.db.session import get_session


# Database session dependency
def get_db() -> Generator[Session, None, None]:
    """
    Get database session dependency.
    
    Yields:
        Database session
    """
    yield from get_session()


# Placeholder cho authentication dependency
# Sẽ được implement sau khi có User model
async def get_current_user():
    """
    Get current authenticated user.
    TODO: Implement sau khi có authentication system.
    """
    pass
