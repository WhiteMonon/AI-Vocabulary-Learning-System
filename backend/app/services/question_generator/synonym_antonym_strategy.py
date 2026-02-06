"""
Strategy cho Content Word - Synonym/Antonym MCQ Question.
Hiện từ → User chọn từ đồng nghĩa/trái nghĩa.
"""
import random
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy


class SynonymAntonymStrategy(QuestionGeneratorStrategy):
    """
    Strategy cho Content Words.
    Generate câu hỏi dạng: chọn synonym/antonym từ 4 options.
    """
    
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate synonym/antonym MCQ question.
        Luôn tạo MCQ với word options, không fallback về definition.
        
        Args:
            vocabulary: Vocabulary cần generate câu hỏi
            difficulty: Mức độ khó
            distractors: Danh sách vocabularies khác làm options
            
        Returns:
            Question data snapshot
        """
        word = vocabulary.word
        
        # Luôn tạo MCQ với word options (không fallback về definition)
        # Correct answer là chính từ này
        correct_answer = word
        
        # Tạo options từ distractors
        options = [correct_answer]
        for dist in distractors:
            if dist.id != vocabulary.id and len(options) < 4:
                options.append(dist.word)
        
        # Đảm bảo có đủ 4 options
        while len(options) < 4:
            options.append(f"word_{len(options)}")
        
        random.shuffle(options)
        
        question_data = {
            "question_type": QuestionType.SYNONYM_ANTONYM_MCQ.value,
            "question_text": f"Which word is CLOSEST in meaning to '{word}'?",
            "correct_answer": correct_answer,
            "word": word,
            "options": options,
            "context_sentence": None,
            "explanation": f"'{word}' is the correct answer.",
        }
        
        return question_data
    
    def get_question_type(self) -> QuestionType:
        """Trả về SYNONYM_ANTONYM_MCQ."""
        return QuestionType.SYNONYM_ANTONYM_MCQ
