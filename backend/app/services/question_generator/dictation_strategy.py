"""
Strategy cho Content Word - Dictation Question.
Nghe audio → User type từ.
"""
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy


class DictationStrategy(QuestionGeneratorStrategy):
    """
    Strategy cho Content Words.
    Generate câu hỏi dạng dictation: nghe audio → type từ.
    """
    
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate dictation question.
        
        Args:
            vocabulary: Vocabulary cần generate câu hỏi
            difficulty: Mức độ khó
            distractors: Không sử dụng cho loại này
            
        Returns:
            Question data snapshot
        """
        # Lấy audio URL từ VocabularyAudio nếu có
        audio_url = None
        if vocabulary.audios:
            audio_url = vocabulary.audios[0].audio_url
        
        question_data = {
            "question_type": QuestionType.DICTATION.value,
            "question_text": "Listen and type the word you hear",
            "correct_answer": vocabulary.word,
            "audio_url": audio_url,
            "options": None,
            "context_sentence": None,
            "explanation": f"Từ đúng là: {vocabulary.word}",
            # Validation: exact match (case-insensitive)
            "validation_mode": "exact",
        }
        
        return question_data
    
    def get_question_type(self) -> QuestionType:
        """Trả về DICTATION."""
        return QuestionType.DICTATION
