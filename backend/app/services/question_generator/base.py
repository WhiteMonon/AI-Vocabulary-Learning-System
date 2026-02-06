"""
Base strategy cho question generation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty


class QuestionGeneratorStrategy(ABC):
    """
    Abstract base class cho question generation strategies.
    Mỗi strategy implement cách generate câu hỏi cho một loại từ vựng.
    """
    
    @abstractmethod
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate question data cho vocabulary.
        
        Args:
            vocabulary: Vocabulary cần generate câu hỏi
            difficulty: Mức độ khó
            distractors: Danh sách vocabularies khác để làm distractor (cho MCQ)
            
        Returns:
            Dict chứa question data snapshot:
            {
                "question_type": QuestionType,
                "question_text": str,
                "correct_answer": str,
                "options": Optional[List[str]],
                "context_sentence": Optional[str],
                "explanation": Optional[str],
                ...
            }
        """
        pass
    
    @abstractmethod
    def get_question_type(self) -> QuestionType:
        """Trả về loại câu hỏi mà strategy này generate."""
        pass
