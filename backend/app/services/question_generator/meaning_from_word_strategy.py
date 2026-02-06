"""
Strategy cho Content Word - Meaning From Word Question.
Hiện từ → User nhập nghĩa.
"""
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy


class MeaningFromWordStrategy(QuestionGeneratorStrategy):
    """
    Strategy cho Content Words.
    Generate câu hỏi dạng: hiện word → user nhập definition.
    """
    
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate meaning from word question.
        
        Args:
            vocabulary: Vocabulary cần generate câu hỏi
            difficulty: Mức độ khó
            distractors: Không sử dụng cho loại này
            
        Returns:
            Question data snapshot
        """
        # Lấy definition để validate answer
        definition = vocabulary.meanings[0].definition if vocabulary.meanings else ""
        
        question_data = {
            "question_type": QuestionType.MEANING_FROM_WORD.value,
            "question_text": f"What does '{vocabulary.word}' mean?",
            "correct_answer": definition,
            "word": vocabulary.word,
            "options": None,
            "context_sentence": None,
            "explanation": f"Nghĩa của '{vocabulary.word}' là: {definition}",
            # Validation sẽ dùng fuzzy matching với definition
            "validation_mode": "fuzzy",
        }
        
        return question_data
    
    def get_question_type(self) -> QuestionType:
        """Trả về MEANING_FROM_WORD."""
        return QuestionType.MEANING_FROM_WORD
