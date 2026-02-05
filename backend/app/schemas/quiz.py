"""
Quiz schemas cho API request/response.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    """Schema cho một câu hỏi trong quiz."""
    id: int = Field(..., description="ID của vocabulary liên quan")
    word: str = Field(..., description="Từ vựng mục tiêu")
    question_text: str = Field(..., description="Nội dung câu hỏi")
    options: Dict[str, str] = Field(..., description="Các lựa chọn (A, B, C, D)")
    correct_answer: str = Field(..., description="Đáp án đúng (A, B, C, D)")
    explanation: str = Field(..., description="Giải thích lý do đúng/sai cho các đáp án")
    grammar_explanation: Optional[str] = Field(None, description="Giải thích các cấu trúc ngữ pháp liên quan")


class QuizSessionResponse(BaseModel):
    """Schema cho một phiên quiz gồm nhiều câu hỏi."""
    questions: List[QuizQuestion] = Field(..., description="Danh sách câu hỏi")


class QuizSubmit(BaseModel):
    """Schema để submit kết quả một câu hỏi quiz."""
    vocabulary_id: int = Field(..., description="ID của vocabulary")
    is_correct: bool = Field(..., description="Người dùng trả lời đúng hay sai")
    time_spent_seconds: int = Field(default=0, ge=0, description="Thời gian trả lời (giây)")
