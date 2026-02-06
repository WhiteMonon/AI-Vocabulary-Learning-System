"""
AIPracticeLog model để track AI practice interactions.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, Integer, DateTime, Text
from sqlalchemy import Index, CheckConstraint, Enum

from app.db.base import BaseModel
from app.models.enums import PracticeType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vocabulary import Vocabulary


class AIPracticeLog(BaseModel, table=True):
    """
    AIPracticeLog model để track mỗi lần user practice với AI.
    Có thể liên kết với vocabulary cụ thể hoặc general practice.
    """
    __tablename__ = "ai_practice_logs"
    
    # Foreign keys
    user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        description="ID của user thực hiện practice"
    )
    vocabulary_id: Optional[int] = Field(
        default=None,
        foreign_key="vocabularies.id",
        nullable=True,
        description="ID của vocabulary được practice (nullable cho general practice)"
    )
    
    # Practice data
    practice_type: PracticeType = Field(
        sa_column=Column(Enum(PracticeType, values_callable=lambda x: [e.value for e in x]), nullable=False),
        description="Loại bài tập AI"
    )
    prompt: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Prompt gửi đến AI"
    )
    ai_response: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Response từ AI"
    )
    user_answer: Optional[str] = Field(
        sa_column=Column(Text, nullable=True),
        default=None,
        description="Câu trả lời của user (nếu có)"
    )
    is_correct: Optional[bool] = Field(
        default=None,
        nullable=True,
        description="User trả lời đúng hay sai (nullable nếu không có đáp án)"
    )
    
    # AI provider info
    ai_provider: str = Field(
        nullable=False,
        description="AI provider được sử dụng (openai, groq, gemini, local)"
    )
    
    # Time tracking
    time_spent_seconds: int = Field(
        sa_column=Column(Integer, nullable=False, default=0),
        default=0,
        description="Thời gian dành cho practice (giây)"
    )
    practiced_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Thời điểm thực hiện practice"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="ai_practice_logs")
    vocabulary: Optional["Vocabulary"] = Relationship(back_populates="ai_practice_logs")
    
    __table_args__ = (
        # Index cho user's practice timeline
        Index("ix_ai_practice_logs_user_date", "user_id", "practiced_at"),
        # Index cho vocabulary practice lookup
        Index("ix_ai_practice_logs_vocab_date", "vocabulary_id", "practiced_at"),
        # Index cho practice type analytics
        Index("ix_ai_practice_logs_type_date", "practice_type", "practiced_at"),
        # Check constraint: time_spent_seconds phải >= 0
        CheckConstraint("time_spent_seconds >= 0", name="ck_practice_time_positive"),
    )
