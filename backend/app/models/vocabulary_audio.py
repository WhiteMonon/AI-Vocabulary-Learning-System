"""
VocabularyAudio model - Lưu audio metadata cho dictation questions.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, Column, String, DateTime
from sqlalchemy import Index

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.vocabulary import Vocabulary


class VocabularyAudio(BaseModel, table=True):
    """
    VocabularyAudio model để lưu audio metadata cho dictation.
    Audio file được generate bởi Edge-TTS và lưu trong filesystem.
    """
    __tablename__ = "vocabulary_audios"
    
    # Foreign key
    vocabulary_id: int = Field(
        foreign_key="vocabularies.id",
        nullable=False,
        description="ID của vocabulary"
    )
    
    # Audio file info
    audio_path: str = Field(
        sa_column=Column(String, nullable=False),
        description="Đường dẫn file trên server: static/audio/{user_id}/{vocab_id}.mp3"
    )
    
    audio_url: str = Field(
        sa_column=Column(String, nullable=False),
        description="URL để serve: /static/audio/{user_id}/{vocab_id}.mp3"
    )
    
    # TTS metadata
    tts_provider: str = Field(
        sa_column=Column(String, nullable=False),
        default="edge-tts",
        description="TTS provider: edge-tts"
    )
    
    voice: str = Field(
        sa_column=Column(String, nullable=False),
        default="en-US-AriaNeural",
        description="Voice name từ Edge-TTS"
    )
    
    language: str = Field(
        sa_column=Column(String, nullable=False),
        default="en-US",
        description="Language code: en-US, en-GB, etc."
    )
    
    # Metadata
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Thời điểm tạo audio"
    )
    
    # Relationships
    vocabulary: "Vocabulary" = Relationship(back_populates="audios")
    
    __table_args__ = (
        # Index cho lookup by vocabulary
        Index("ix_vocabulary_audios_vocabulary_id", "vocabulary_id"),
    )
