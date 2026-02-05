"""
Dependency injection functions.
Cung cấp common dependencies cho FastAPI endpoints.
"""
from typing import Generator
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.APP_NAME}/api/v1/auth/login") # Adjust path if needed


# Database session dependency
def get_db() -> Generator[Session, None, None]:
    """
    Get database session dependency.
    
    Yields:
        Database session
    """
    yield from get_session()


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Lấy thông tin user hiện tại từ JWT token.
    
    Args:
        db: Database session
        token: JWT access token
        
    Returns:
        User object nếu token hợp lệ
        
    Raises:
        HTTPException: Nếu token không hợp lệ hoặc user không tồn tại
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
        
    return user
