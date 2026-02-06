"""
Review schemas cho API request/response.
Hỗ trợ context-based review với question snapshots và telemetry tracking.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.enums import QuestionType, QuestionDifficulty, ReviewQuality


# ============= Question Schemas =============

class QuestionResponse(BaseModel):
    """
    Schema cho một câu hỏi được generate trong review session.
    Bao gồm snapshot đầy đủ và metadata.
    """
    question_instance_id: str = Field(..., description="UUID duy nhất của question instance")
    vocabulary_id: int = Field(..., description="ID của vocabulary liên quan")
    question_type: QuestionType = Field(..., description="Loại câu hỏi")
    difficulty: QuestionDifficulty = Field(..., description="Mức độ khó")
    
    # Question content (snapshot)
    question_text: str = Field(..., description="Nội dung câu hỏi")
    options: Optional[List[str]] = Field(None, description="Các lựa chọn (cho MCQ)")
    context_sentence: Optional[str] = Field(None, description="Câu ngữ cảnh (cho Fill Blank)")
    
    # Metadata
    confusion_pair_group: Optional[str] = Field(None, description="Nhóm confusion pair")
    
    class Config:
        from_attributes = True


class QuestionSubmission(BaseModel):
    """
    Schema cho việc submit câu trả lời của một question.
    Bao gồm telemetry tracking chi tiết.
    """
    question_instance_id: str = Field(..., description="UUID của question instance")
    user_answer: str = Field(..., description="Câu trả lời của user")
    
    # Telemetry data
    time_spent_ms: int = Field(..., ge=0, description="Thời gian trả lời (milliseconds)")
    answer_change_count: int = Field(default=0, ge=0, description="Số lần thay đổi câu trả lời")
    
    class Config:
        from_attributes = True


# ============= Session Schemas =============

class ReviewSessionCreate(BaseModel):
    """Schema để tạo review session mới."""
    mode: str = Field(default="due", description="Mode: 'due' hoặc 'new'")
    max_questions: int = Field(default=20, ge=1, le=100, description="Số câu hỏi tối đa")


class ReviewSessionResponse(BaseModel):
    """Schema cho review session response."""
    session_id: int = Field(..., description="ID của session")
    status: str = Field(..., description="Trạng thái session")
    total_questions: int = Field(..., description="Tổng số câu hỏi")
    questions: List[QuestionResponse] = Field(..., description="Danh sách câu hỏi")
    started_at: datetime = Field(..., description="Thời điểm bắt đầu")
    
    class Config:
        from_attributes = True


class BatchSubmitRequest(BaseModel):
    """Schema cho batch submit nhiều câu trả lời."""
    submissions: List[QuestionSubmission] = Field(..., min_length=1, description="Danh sách submissions")


class SubmitResponse(BaseModel):
    """Schema cho response sau khi submit."""
    question_instance_id: str
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None


class BatchSubmitResponse(BaseModel):
    """Schema cho batch submit response."""
    results: List[SubmitResponse]
    session_summary: Dict[str, Any] = Field(..., description="Tóm tắt session")


class SessionSummaryResponse(BaseModel):
    """Schema cho session summary sau khi hoàn thành."""
    session_id: int
    total_questions: int
    correct_count: int
    accuracy: float
    total_time_seconds: int
    completed_at: datetime
    
    class Config:
        from_attributes = True
