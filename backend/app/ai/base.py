from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.ai.schemas import AIQuestion, AIEvaluation
from app.models.vocabulary import Vocabulary
from app.models.enums import PracticeType

class AIProvider(ABC):
    """Abstract Base Class cho các AI Providers."""

    @abstractmethod
    async def generate_question(
        self, 
        vocab: Vocabulary, 
        practice_type: PracticeType = PracticeType.MULTIPLE_CHOICE
    ) -> AIQuestion:
        """
        Sinh câu hỏi dựa trên từ vựng và loại bài tập.
        """
        pass

    @abstractmethod
    async def evaluate_answer(
        self, 
        question: AIQuestion, 
        answer: str
    ) -> AIEvaluation:
        """
        Đánh giá câu trả lời của người dùng.
        """
        pass
