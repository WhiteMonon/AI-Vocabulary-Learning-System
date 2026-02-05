"""
Vocabulary schemas cho API request/response.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.enums import DifficultyLevel, ReviewQuality


# ============= Request Schemas =============

class VocabularyCreate(BaseModel):
    """Schema để tạo vocabulary mới."""
    word: str = Field(..., min_length=1, max_length=200, description="Từ vựng cần học")
    definition: str = Field(..., min_length=1, description="Định nghĩa của từ")
    example_sentence: Optional[str] = Field(None, description="Câu ví dụ sử dụng từ")
    difficulty_level: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM,
        description="Mức độ khó của vocabulary"
    )
    
    @field_validator('word')
    @classmethod
    def word_must_not_be_empty(cls, v: str) -> str:
        """Validate word không được chỉ chứa khoảng trắng."""
        if not v.strip():
            raise ValueError('Word không được để trống')
        return v.strip()
    
    @field_validator('definition')
    @classmethod
    def definition_must_not_be_empty(cls, v: str) -> str:
        """Validate definition không được chỉ chứa khoảng trắng."""
        if not v.strip():
            raise ValueError('Definition không được để trống')
        return v.strip()


class VocabularyUpdate(BaseModel):
    """Schema để update vocabulary."""
    word: Optional[str] = Field(None, min_length=1, max_length=200, description="Từ vựng cần học")
    definition: Optional[str] = Field(None, min_length=1, description="Định nghĩa của từ")
    example_sentence: Optional[str] = Field(None, description="Câu ví dụ sử dụng từ")
    difficulty_level: Optional[DifficultyLevel] = Field(None, description="Mức độ khó của vocabulary")
    
    @field_validator('word')
    @classmethod
    def word_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate word không được chỉ chứa khoảng trắng."""
        if v is not None and not v.strip():
            raise ValueError('Word không được để trống')
        return v.strip() if v else v
    
    @field_validator('definition')
    @classmethod
    def definition_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate definition không được chỉ chứa khoảng trắng."""
        if v is not None and not v.strip():
            raise ValueError('Definition không được để trống')
        return v.strip() if v else v


class VocabularyReview(BaseModel):
    """Schema để review vocabulary (SRS update)."""
    review_quality: ReviewQuality = Field(..., description="Chất lượng review theo SM-2 (0-3)")
    time_spent_seconds: int = Field(
        default=0,
        ge=0,
        description="Thời gian dành cho review (giây)"
    )


# ============= Response Schemas =============

class VocabularyResponse(BaseModel):
    """Schema cho vocabulary response."""
    id: int
    user_id: int
    word: str
    definition: str
    example_sentence: Optional[str]
    difficulty_level: DifficultyLevel
    
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
    items: list[VocabularyResponse]
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
    by_difficulty: dict[str, int]
