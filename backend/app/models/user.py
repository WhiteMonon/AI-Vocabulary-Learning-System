"""
User model với authentication và authorization.
"""
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel, Column, String
from sqlalchemy import Index

from app.db.base import BaseModel
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.vocabulary import Vocabulary
    from app.models.review_history import ReviewHistory
    from app.models.ai_practice_log import AIPracticeLog


class User(BaseModel, table=True):
    """
    User model cho authentication và authorization.
    Mỗi user có thể có nhiều vocabularies, review histories và AI practice logs.
    """
    __tablename__ = "users"
    
    # Authentication fields
    email: str = Field(
        sa_column=Column(String, unique=True, nullable=False),
        description="Email của user (unique)"
    )
    username: str = Field(
        sa_column=Column(String, unique=True, nullable=False),
        description="Username của user (unique)"
    )
    hashed_password: str = Field(
        nullable=False,
        description="Hashed password (bcrypt)"
    )
    
    # Profile fields
    full_name: Optional[str] = Field(
        default=None,
        description="Tên đầy đủ của user"
    )
    
    # Authorization fields
    role: UserRole = Field(
        default=UserRole.USER,
        nullable=False,
        description="Role của user trong hệ thống"
    )
    
    # Status fields
    is_active: bool = Field(
        default=True,
        nullable=False,
        description="User có đang active không"
    )
    is_verified: bool = Field(
        default=False,
        nullable=False,
        description="Email đã được verify chưa"
    )
    
    # Relationships
    vocabularies: List["Vocabulary"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    review_histories: List["ReviewHistory"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    ai_practice_logs: List["AIPracticeLog"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_username", "username"),
    )
