"""
Vocabulary schemas cho API request/response.
Updated để hỗ trợ multiple meanings và import/export.
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator

from app.models.enums import WordType, MeaningSource, ReviewQuality


# ============= Meaning Schemas =============

class MeaningCreate(BaseModel):
    """Schema để tạo meaning mới."""
    definition: str = Field(..., min_length=1, description="Định nghĩa của từ")
    example_sentence: Optional[str] = Field(None, description="Câu ví dụ thực tế (optional)")

    
    @field_validator('definition')
    @classmethod
    def definition_must_not_be_empty(cls, v: str) -> str:
        """Validate definition không được chỉ chứa khoảng trắng."""
        if not v.strip():
            raise ValueError('Definition không được để trống')
        return v.strip()


class MeaningResponse(BaseModel):
    """Schema cho meaning response."""
    id: int
    definition: str
    meaning_source: MeaningSource
    is_auto_generated: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContextResponse(BaseModel):
    """Schema cho vocabulary context response."""
    id: int
    sentence: str
    translation: Optional[str]
    ai_provider: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Vocabulary Request Schemas =============

class VocabularyCreate(BaseModel):
    """Schema để tạo vocabulary mới."""
    word: str = Field(..., min_length=1, max_length=200, description="Từ vựng cần học")
    meanings: List[MeaningCreate] = Field(..., min_length=1, description="Danh sách meanings")
    word_type: Optional[WordType] = Field(None, description="Override word type (None = auto classify)")
    
    @field_validator('word')
    @classmethod
    def word_must_not_be_empty(cls, v: str) -> str:
        """Validate word không được chỉ chứa khoảng trắng."""
        if not v.strip():
            raise ValueError('Word không được để trống')
        return v.strip()


class VocabularyUpdate(BaseModel):
    """Schema để update vocabulary."""
    word: Optional[str] = Field(None, min_length=1, max_length=200, description="Từ vựng cần học")
    word_type: Optional[WordType] = Field(None, description="Override word type")
    
    @field_validator('word')
    @classmethod
    def word_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate word không được chỉ chứa khoảng trắng."""
        if v is not None and not v.strip():
            raise ValueError('Word không được để trống')
        return v.strip() if v else v


class VocabularyReview(BaseModel):
    """Schema để review vocabulary (SRS update)."""
    review_quality: ReviewQuality = Field(..., description="Chất lượng review theo SM-2 (0-3)")
    time_spent_seconds: int = Field(
        default=0,
        ge=0,
        description="Thời gian dành cho review (giây)"
    )


class VocabularyReviewItem(BaseModel):
    """Item trong batch review request."""
    vocabulary_id: int
    review_quality: ReviewQuality
    time_spent_seconds: int = Field(default=0, ge=0)


class BatchReviewRequest(BaseModel):
    """Schema cho batch review."""
    items: List[VocabularyReviewItem]


# ============= Import/Export Schemas =============

class VocabularyImportRequest(BaseModel):
    """Schema cho import request."""
    content: str = Field(..., description="Nội dung file TXT (word|definition|example)")
    auto_fetch_meaning: bool = Field(True, description="Tự động fetch meaning từ API nếu không có")


class ImportResultResponse(BaseModel):
    """Schema cho kết quả import."""
    total_processed: int
    new_words: int
    merged_meanings: int
    auto_generated_count: int
    failed_auto_meaning: List[str]
    warnings: List[str]
    errors: List[str]
    created_vocab_ids: List[int] = []


class ExportFormat(BaseModel):
    """Schema cho export format."""
    format: Literal["json", "txt", "csv"] = Field("json", description="Format export")


# ============= Response Schemas =============

class VocabularyResponse(BaseModel):
    """Schema cho vocabulary response."""
    id: int
    user_id: int
    word: str
    word_type: WordType
    is_word_type_manual: bool
    meanings: List[MeaningResponse]
    contexts: List[ContextResponse] = []
    
    # SRS fields
    easiness_factor: float
    interval: int
    repetitions: int
    next_review_date: datetime
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VocabularyListResponse(BaseModel):
    """Schema cho danh sách vocabularies với pagination."""
    items: List[VocabularyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class VocabularyStatsResponse(BaseModel):
    """Schema cho thống kê vocabulary của user."""
    total_vocabularies: int
    due_today: int
    learned: int  # repetitions > 0
    learning: int  # repetitions == 0
    by_word_type: dict[str, int]
