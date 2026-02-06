"""
DictionaryCache model - Cache API results để giảm external API calls.
"""
from datetime import datetime, timedelta
from sqlmodel import Field, Column, String, DateTime
from sqlalchemy import Index

from app.db.base import BaseModel
from app.models.enums import MeaningSource


class DictionaryCache(BaseModel, table=True):
    """
    Cache cho Dictionary API và Translation API results.
    TTL mặc định: 30 ngày.
    """
    __tablename__ = "dictionary_cache"
    
    # Unique word để lookup
    word: str = Field(
        sa_column=Column(String, nullable=False, unique=True),
        description="Từ cần tra cứu (normalized: lowercase, trimmed)"
    )
    
    # Cached content
    definition: str = Field(
        sa_column=Column(String, nullable=False),
        description="Definition được cache"
    )
    
    # Source tracking
    source: MeaningSource = Field(
        nullable=False,
        description="Nguồn của definition: dictionary_api hoặc auto_translate"
    )
    
    # TTL management
    fetched_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Thời điểm fetch từ API"
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        description="Thời điểm hết hạn cache"
    )
    
    __table_args__ = (
        Index("ix_dictionary_cache_word", "word"),
        Index("ix_dictionary_cache_expires_at", "expires_at"),
    )
    
    @classmethod
    def create_with_ttl(
        cls, 
        word: str, 
        definition: str, 
        source: MeaningSource,
        ttl_days: int = 30
    ) -> "DictionaryCache":
        """Factory method để tạo cache entry với TTL."""
        now = datetime.utcnow()
        return cls(
            word=word.lower().strip(),
            definition=definition,
            source=source,
            fetched_at=now,
            expires_at=now + timedelta(days=ttl_days)
        )
