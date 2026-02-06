"""
Vocabulary model với SRS (Spaced Repetition System) fields.
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, String, Float, Integer, DateTime, Boolean
from sqlalchemy import Index, UniqueConstraint, CheckConstraint, Enum

from app.db.base import BaseModel
from app.models.enums import WordType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.review_history import ReviewHistory
    from app.models.ai_practice_log import AIPracticeLog
    from app.models.vocabulary_meaning import VocabularyMeaning
    from app.models.generated_question import GeneratedQuestion
    from app.models.vocabulary_context import VocabularyContext
    from app.models.vocabulary_audio import VocabularyAudio


class Vocabulary(BaseModel, table=True):
    """
    Vocabulary model với SRS algorithm fields (SM-2).
    Mỗi vocabulary thuộc về một user và có thể có nhiều meanings, review histories và AI practice logs.
    """
    __tablename__ = "vocabularies"
    
    # Foreign key
    user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        description="ID của user sở hữu vocabulary này"
    )
    
    # Vocabulary content - normalized (lowercase, trimmed)
    word: str = Field(
        sa_column=Column(String, nullable=False),
        description="Từ vựng cần học (normalized: lowercase, trimmed)"
    )
    
    # Word classification
    word_type: WordType = Field(
        sa_column=Column(Enum(WordType, values_callable=lambda x: [e.value for e in x]), nullable=False),
        default=WordType.CONTENT_WORD,
        description="Phân loại từ: function_word hoặc content_word"
    )
    is_word_type_manual: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False),
        default=False,
        description="True nếu user đã override word_type manually"
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
    last_review_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        default=None,
        description="Ngày review lần cuối"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="vocabularies")
    meanings: List["VocabularyMeaning"] = Relationship(
        back_populates="vocabulary",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    review_histories: List["ReviewHistory"] = Relationship(
        back_populates="vocabulary",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    ai_practice_logs: List["AIPracticeLog"] = Relationship(
        back_populates="vocabulary",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    generated_questions: List["GeneratedQuestion"] = Relationship(
        back_populates="vocabulary",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    contexts: List["VocabularyContext"] = Relationship(
        back_populates="vocabulary",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    audios: List["VocabularyAudio"] = Relationship(
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
