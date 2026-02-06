"""
Strategy cho Content Word - Definition MCQ Question.
Hiện từ → User chọn definition đúng từ 4 options.
"""
import random
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy


class DefinitionMCQStrategy(QuestionGeneratorStrategy):
    """
    Strategy cho Content Words.
    Generate câu hỏi dạng: hiện word → chọn definition đúng từ 4 options.
    """
    
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate definition MCQ question.
        
        Args:
            vocabulary: Vocabulary cần generate câu hỏi
            difficulty: Mức độ khó
            distractors: Danh sách vocabularies khác làm options
            
        Returns:
            Question data snapshot
        """
        word = vocabulary.word
        
        # Lấy definition của vocabulary này
        correct_answer = vocabulary.meanings[0].definition if vocabulary.meanings else f"Definition of {word}"
        
        # Tạo options từ distractors
        options = [correct_answer]
        for dist in distractors:
            if dist.id != vocabulary.id and len(options) < 4:
                if dist.meanings:
                    dist_def = dist.meanings[0].definition
                    if dist_def and dist_def not in options:
                        options.append(dist_def)
        
        # Đảm bảo có đủ 4 options
        while len(options) < 4:
            options.append(f"Incorrect definition {len(options)}")
        
        random.shuffle(options)
        
        question_data = {
            "question_type": QuestionType.DEFINITION_MCQ.value,
            "question_text": f"What is the meaning of '{word}'?",
            "correct_answer": correct_answer,
            "word": word,
            "options": options,
            "context_sentence": None,
            "explanation": f"Nghĩa đúng của '{word}' là: {correct_answer}",
        }
        
        return question_data
    
    def get_question_type(self) -> QuestionType:
        """Trả về DEFINITION_MCQ."""
        return QuestionType.DEFINITION_MCQ
