"""
Generated Question model để lưu snapshot của mỗi câu hỏi trong review session.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING, Dict, Any
from sqlmodel import Field, Relationship, Column, String, JSON, Boolean, Integer
from sqlalchemy import Index, Enum
import uuid

from app.db.base import BaseModel
from app.models.enums import QuestionType, QuestionDifficulty

if TYPE_CHECKING:
    from app.models.review_session import ReviewSession
    from app.models.vocabulary import Vocabulary
    from app.models.user import User


class GeneratedQuestion(BaseModel, table=True):
    """
    GeneratedQuestion model để lưu snapshot của mỗi câu hỏi được generate.
    Đảm bảo history review không bị sai khi vocabulary data thay đổi.
    """
    __tablename__ = "generated_questions"
    
    # Question Instance ID (UUID)
    question_instance_id: str = Field(
        sa_column=Column(String, nullable=False, unique=True, index=True),
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID duy nhất cho question instance"
    )
    
    # Foreign keys
    session_id: int = Field(
        foreign_key="review_sessions.id",
        nullable=False,
        description="ID của review session"
    )
    
    user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        description="ID của user"
    )
    
    vocabulary_id: int = Field(
        foreign_key="vocabularies.id",
        nullable=False,
        description="ID của vocabulary liên quan"
    )
    
    # Question metadata
    question_type: QuestionType = Field(
        sa_column=Column(Enum(QuestionType, values_callable=lambda x: [e.value for e in x]), nullable=False),
        description="Loại câu hỏi"
    )
    
    difficulty: QuestionDifficulty = Field(
        sa_column=Column(Enum(QuestionDifficulty, values_callable=lambda x: [e.value for e in x]), nullable=False),
        default=QuestionDifficulty.MEDIUM,
        description="Mức độ khó của câu hỏi"
    )
    
    question_variant: Optional[str] = Field(
        sa_column=Column(String, nullable=True),
        default=None,
        description="Biến thể của câu hỏi (để tránh lặp lại)"
    )
    
    # Question Snapshot (JSON)
    question_data: Dict[str, Any] = Field(
        sa_column=Column(JSON, nullable=False),
        description="""
        Snapshot đầy đủ của câu hỏi, bao gồm:
        - question_text: Nội dung câu hỏi
        - correct_answer: Đáp án đúng
        - options: Các lựa chọn (nếu MCQ)
        - context_sentence: Câu ngữ cảnh (nếu Fill Blank)
        - error_position: Vị trí lỗi (nếu Error Detection)
        - explanation: Giải thích (optional)
        """
    )
    
    # Answer & Evaluation
    user_answer: Optional[str] = Field(
        sa_column=Column(String, nullable=True),
        default=None,
        description="Câu trả lời của user"
    )
    
    is_correct: Optional[bool] = Field(
        sa_column=Column(Boolean, nullable=True),
        default=None,
        description="User trả lời đúng hay sai"
    )
    
    # Telemetry Data
    time_spent_ms: Optional[int] = Field(
        sa_column=Column(Integer, nullable=True),
        default=None,
        description="Thời gian trả lời (milliseconds)"
    )
    
    answer_change_count: Optional[int] = Field(
        sa_column=Column(Integer, nullable=True),
        default=0,
        description="Số lần user thay đổi câu trả lời"
    )
    
    # Advanced tracking (cho Function Words)
    confusion_pair_group: Optional[str] = Field(
        sa_column=Column(String, nullable=True),
        default=None,
        description="Nhóm confusion pair (e.g., 'at_in_on' cho prepositions)"
    )
    
    pattern_id: Optional[str] = Field(
        sa_column=Column(String, nullable=True),
        default=None,
        description="Pattern ID cho Function Word (e.g., 'arrive_at_pattern')"
    )
    
    # Relationships
    session: "ReviewSession" = Relationship(back_populates="questions")
    user: "User" = Relationship(back_populates="generated_questions")
    vocabulary: "Vocabulary" = Relationship(back_populates="generated_questions")
    
    __table_args__ = (
        # Index cho session queries
        Index("ix_generated_questions_session", "session_id"),
        # Index cho user analytics
        Index("ix_generated_questions_user_vocab", "user_id", "vocabulary_id"),
        # Index cho confusion pair analysis
        Index("ix_generated_questions_confusion", "confusion_pair_group"),
    )
