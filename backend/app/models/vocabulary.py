"""
Vocabulary model với SRS (Spaced Repetition System) fields.
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, String, Float, Integer, DateTime
from sqlalchemy import Index, UniqueConstraint, CheckConstraint

from app.db.base import BaseModel
from app.models.enums import DifficultyLevel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.review_history import ReviewHistory
    from app.models.ai_practice_log import AIPracticeLog


class Vocabulary(BaseModel, table=True):
    """
    Vocabulary model với SRS algorithm fields (SM-2).
    Mỗi vocabulary thuộc về một user và có thể có nhiều review histories và AI practice logs.
    """
    __tablename__ = "vocabularies"
    
    # Foreign key
    user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        description="ID của user sở hữu vocabulary này"
    )
    
    # Vocabulary content
    word: str = Field(
        sa_column=Column(String, nullable=False),
        description="Từ vựng cần học"
    )
    definition: str = Field(
        nullable=False,
        description="Định nghĩa của từ"
    )
    example_sentence: Optional[str] = Field(
        default=None,
        description="Câu ví dụ sử dụng từ"
    )
    
    # Difficulty
    difficulty_level: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM,
        nullable=False,
        description="Mức độ khó của vocabulary"
    )
    
    # SRS Algorithm fields (SM-2)
    easiness_factor: float = Field(
        sa_column=Column(Float, nullable=False, default=2.5),
        default=2.5,
        description="Hệ số dễ dàng (EF) trong SM-2, min=1.3"
    )
    interval: int = Field(
        sa_column=Column(Integer, nullable=False, default=0),
        default=0,
        description="Khoảng thời gian đến lần review tiếp theo (ngày)"
    )
    repetitions: int = Field(
        sa_column=Column(Integer, nullable=False, default=0),
        default=0,
        description="Số lần review thành công liên tiếp"
    )
    next_review_date: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Ngày review tiếp theo"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="vocabularies")
    review_histories: List["ReviewHistory"] = Relationship(
        back_populates="vocabulary",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    ai_practice_logs: List["AIPracticeLog"] = Relationship(
        back_populates="vocabulary",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    __table_args__ = (
        # Composite index cho daily review queries
        Index("ix_vocabularies_user_next_review", "user_id", "next_review_date"),
        # Composite index cho word lookup
        Index("ix_vocabularies_user_word", "user_id", "word"),
        # Unique constraint: một user không thể có 2 vocabulary giống nhau
        UniqueConstraint("user_id", "word", name="uq_user_vocabulary"),
        # Check constraint: easiness_factor phải >= 1.3 (theo SM-2)
        CheckConstraint("easiness_factor >= 1.3", name="ck_easiness_factor_min"),
    )
