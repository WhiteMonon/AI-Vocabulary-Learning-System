from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from app.models.enums import PracticeType

class AIQuestion(BaseModel):
    """Schema cho câu hỏi được sinh ra bởi AI."""
    question_text: str = Field(..., description="Nội dung câu hỏi")
    options: Optional[Dict[str, str]] = Field(None, description="Các lựa chọn (cho trắc nghiệm)")
    correct_answer: str = Field(..., description="Đáp án đúng")
    explanation: Optional[str] = Field(None, description="Giải thích cho đáp án")
    grammar_explanation: Optional[str] = Field(None, description="Giải thích các cấu trúc ngữ pháp")
    practice_type: PracticeType = Field(..., description="Loại bài tập")

class AIEvaluation(BaseModel):
    """Schema cho kết quả đánh giá câu trả lời từ AI."""
    is_correct: bool = Field(..., description="Câu trả lời có đúng hay không")
    feedback: str = Field(..., description="Phản hồi từ AI về câu trả lời")
    score: float = Field(..., description="Điểm số (0.0 đến 1.0)")

class AIChatMessage(BaseModel):
    """Schema cho một tin nhắn trong hội thoại AI."""
    role: str = Field(..., description="Vai trò của người gửi (user, assistant, system)")
    content: str = Field(..., description="Nội dung tin nhắn")

class AIChatRequest(BaseModel):
    """Schema cho yêu cầu chat với AI."""
    messages: List[AIChatMessage] = Field(..., description="Danh sách lịch sử tin nhắn")
    vocab_id: Optional[str] = Field(None, description="ID của từ vựng đang luyện tập (nếu có)")
    practice_type: Optional[PracticeType] = Field(None, description="Loại bài tập liên quan")
