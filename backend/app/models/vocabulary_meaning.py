"""
VocabularyMeaning model - Multiple meanings cho mỗi vocabulary.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, String, Boolean
from sqlalchemy import Index, Enum

from app.db.base import BaseModel
from app.models.enums import MeaningSource

if TYPE_CHECKING:
    from app.models.vocabulary import Vocabulary


class VocabularyMeaning(BaseModel, table=True):
    """
    Meaning của vocabulary (one-to-many relationship).
    Mỗi vocabulary có thể có nhiều meanings.
    """
    __tablename__ = "vocabulary_meanings"
    
    # Foreign key
    vocabulary_id: int = Field(
        foreign_key="vocabularies.id",
        nullable=False,
        description="ID của vocabulary chứa meaning này"
    )
    
    # Content
    definition: str = Field(
        sa_column=Column(String, nullable=False),
        description="Định nghĩa của từ"
    )
    
    # Auto Meaning Generation tracking
    meaning_source: MeaningSource = Field(
        sa_column=Column(Enum(MeaningSource, values_callable=lambda x: [e.value for e in x]), nullable=False),
        default=MeaningSource.MANUAL,
        description="Nguồn gốc của meaning: manual, dictionary_api, auto_translate"
    )
    is_auto_generated: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False),
        default=False,
        description="True nếu meaning được tự động generate từ API"
    )
    
    # Relationships
    vocabulary: "Vocabulary" = Relationship(back_populates="meanings")
    
    __table_args__ = (
        # Index cho lookup by vocabulary
        Index("ix_vocabulary_meanings_vocabulary_id", "vocabulary_id"),
    )
