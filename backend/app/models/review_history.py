"""
ReviewHistory model để track learning progress.
"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, Integer, DateTime
from sqlalchemy import Index, CheckConstraint, Enum

from app.db.base import BaseModel
from app.models.enums import ReviewQuality

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vocabulary import Vocabulary


class ReviewHistory(BaseModel, table=True):
    """
    ReviewHistory model để track mỗi lần user review một vocabulary.
    Dùng để analytics và cải thiện SRS algorithm.
    """
    __tablename__ = "review_histories"
    
    # Foreign keys
    user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        description="ID của user thực hiện review"
    )
    vocabulary_id: int = Field(
        foreign_key="vocabularies.id",
        nullable=False,
        description="ID của vocabulary được review"
    )
    
    # Review data
    review_quality: ReviewQuality = Field(
        nullable=False,
        description="Chất lượng review theo SM-2 (0-3)"
    )
    time_spent_seconds: int = Field(
        sa_column=Column(Integer, nullable=False, default=0),
        default=0,
        description="Thời gian dành cho review (giây)"
    )
    
    # Timestamp
    reviewed_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Thời điểm thực hiện review"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="review_histories")
    vocabulary: "Vocabulary" = Relationship(back_populates="review_histories")
    
    __table_args__ = (
        # Composite index cho analytics queries
        Index("ix_review_histories_user_vocab_date", "user_id", "vocabulary_id", "reviewed_at"),
        # Composite index cho user's review timeline
        Index("ix_review_histories_user_date", "user_id", "reviewed_at"),
        # Check constraint: time_spent_seconds phải >= 0
        CheckConstraint("time_spent_seconds >= 0", name="ck_time_spent_positive"),
    )
