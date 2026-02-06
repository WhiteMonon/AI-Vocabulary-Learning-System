"""
Strategy cho Content Word - Meaning Input Question.
Hiện nghĩa → User nhập từ.
"""
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy


class MeaningQuestionStrategy(QuestionGeneratorStrategy):
    """
    Strategy cho Content Words.
    Generate câu hỏi dạng: hiện definition → user nhập word.
    """
    
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate meaning input question.
        
        Args:
            vocabulary: Vocabulary cần generate câu hỏi
            difficulty: Mức độ khó (không ảnh hưởng nhiều cho loại này)
            distractors: Không sử dụng cho Meaning Input
            
        Returns:
            Question data snapshot
        """
        # Lấy definition đầu tiên (hoặc random nếu có nhiều meanings)
        definition = vocabulary.meanings[0].definition if vocabulary.meanings else None
        
        # Validation: nếu definition rỗng, tạo fallback text
        if not definition or not definition.strip():
            definition = f"Từ vựng: {vocabulary.word}"
        
        question_data = {
            "question_type": QuestionType.MEANING_INPUT,
            "question_text": definition,
            "correct_answer": vocabulary.word,
            "options": None,
            "context_sentence": None,
            "explanation": f"Từ đúng là: {vocabulary.word}",
        }
        
        return question_data
    
    def get_question_type(self) -> QuestionType:
        """Trả về MEANING_INPUT."""
        return QuestionType.MEANING_INPUT
