"""
Review Session model để track phiên ôn tập của user.
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, String, DateTime
from sqlalchemy import Index

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.generated_question import GeneratedQuestion


class ReviewSession(BaseModel, table=True):
    """
    ReviewSession model để track một phiên ôn tập của user.
    Mỗi session chứa nhiều generated questions với snapshots.
    """
    __tablename__ = "review_sessions"
    
    # Foreign key
    user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        description="ID của user thực hiện session"
    )
    
    # Session metadata
    status: str = Field(
        sa_column=Column(String, nullable=False, default="in_progress"),
        default="in_progress",
        description="Trạng thái session: in_progress, completed, abandoned"
    )
    
    total_questions: int = Field(
        default=0,
        description="Tổng số câu hỏi trong session"
    )
    
    correct_count: int = Field(
        default=0,
        description="Số câu trả lời đúng"
    )
    
    # Timestamps
    started_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Thời điểm bắt đầu session"
    )
    
    completed_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        default=None,
        description="Thời điểm hoàn thành session"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="review_sessions")
    questions: List["GeneratedQuestion"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    __table_args__ = (
        # Index cho user's session history
        Index("ix_review_sessions_user_started", "user_id", "started_at"),
        # Index cho active sessions
        Index("ix_review_sessions_status", "status"),
    )
