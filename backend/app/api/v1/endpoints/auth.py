from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import Token, UserOut, UserRegister, UserLogin

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserRegister
) -> Any:
    """
    Đăng ký người dùng mới.
    """
    # Kiểm tra email đã tồn tại chưa
    user = db.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email này đã được đăng ký.",
        )
    
    # Kiểm tra username đã tồn tại chưa
    user = db.exec(select(User).where(User.username == user_in.username)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Username này đã được sử dụng.",
        )

    # Tạo user mới
    db_obj = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Đăng nhập bằng OAuth2 compatible token login.
    """
    print(f"DEBUG: Login attempt for username: {form_data.username}")
    # Tìm user theo email hoặc username (form_data.username có thể là email)
    user = db.exec(select(User).where(
        (User.email == form_data.username) | (User.username == form_data.username)
    )).first()
    
    if not user:
        print(f"DEBUG: User not found: {form_data.username}")
    elif not security.verify_password(form_data.password, user.hashed_password):
        print(f"DEBUG: Password mismatch for user: {user.email}")
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản đã bị khóa")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Lấy thông tin người dùng hiện tại.
    """
    return current_user
