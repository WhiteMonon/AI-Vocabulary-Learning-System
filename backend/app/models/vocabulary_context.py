"""
VocabularyContext model - Lưu trữ câu ví dụ được AI generate cho vocabulary.
Tách biệt khỏi VocabularyMeaning để không làm ô nhiễm dữ liệu của user.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, String, DateTime
from sqlalchemy import Index

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.vocabulary import Vocabulary


class VocabularyContext(BaseModel, table=True):
    """
    VocabularyContext model để lưu câu ví dụ AI-generated.
    Một vocabulary có thể có nhiều contexts (để đa dạng hóa câu hỏi).
    """
    __tablename__ = "vocabulary_contexts"
    
    # Foreign key
    vocabulary_id: int = Field(
        foreign_key="vocabularies.id",
        nullable=False,
        description="ID của vocabulary"
    )
    
    # Content
    sentence: str = Field(
        sa_column=Column(String, nullable=False),
        description="Câu ví dụ chứa từ vựng"
    )
    
    translation: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
        description="Bản dịch của câu ví dụ (optional)"
    )
    
    # Metadata
    ai_provider: str = Field(
        sa_column=Column(String, nullable=False, default="system"),
        default="system",
        description="AI provider đã generate câu này (openai, groq, gemini, system, import)"
    )
    
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Thời điểm tạo context"
    )
    
    # Relationships
    vocabulary: "Vocabulary" = Relationship(back_populates="contexts")
    
    __table_args__ = (
        # Index cho lookup by vocabulary
        Index("ix_vocabulary_contexts_vocabulary_id", "vocabulary_id"),
        # Index cho analytics by provider
        Index("ix_vocabulary_contexts_provider", "ai_provider"),
    )
