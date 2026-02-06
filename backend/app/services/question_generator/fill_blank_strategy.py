"""
Strategy cho Function Word - Fill Blank Question.
Hiện câu với chỗ trống → User điền từ.
"""
import random
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy


# Confusion pairs cho prepositions
PREPOSITION_CONFUSION_GROUPS = {
    "at": ["in", "on", "to"],
    "in": ["at", "on", "into"],
    "on": ["at", "in", "onto"],
    "for": ["since", "from", "to"],
    "since": ["for", "from"],
    "to": ["for", "at", "into"],
}


class FillBlankStrategy(QuestionGeneratorStrategy):
    """
    Strategy cho Function Words - Fill in the Blank.
    Sử dụng example_sentence từ vocabulary meanings.
    """
    
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate fill-in-the-blank question từ example sentence.
        
        Args:
            vocabulary: Function Word cần generate câu hỏi
            difficulty: Mức độ khó
            distractors: Danh sách vocabularies khác (ưu tiên confusion pairs)
            
        Returns:
            Question data snapshot
        """
        word = vocabulary.word
        
        # Lấy example sentence từ VocabularyContext (thay vì từ meanings)
        example_sentence = None
        if vocabulary.contexts:
            # Lấy random context để tạo sự đa dạng
            valid_contexts = [c.sentence for c in vocabulary.contexts]
            if valid_contexts:
                example_sentence = random.choice(valid_contexts)
        
        # Fallback: nếu không có context, delegate sang MeaningQuestionStrategy
        if not example_sentence:
            from app.services.question_generator.meaning_strategy import MeaningQuestionStrategy
            meaning_strategy = MeaningQuestionStrategy()
            return meaning_strategy.generate(vocabulary, difficulty, distractors)
        
        # Tạo context sentence với blank
        context_sentence = example_sentence.replace(word, "___")
        
        # Xác định confusion pair group
        confusion_group = None
        if word in PREPOSITION_CONFUSION_GROUPS:
            confusion_group = f"preposition_{word}"
        
        question_data = {
            "question_type": QuestionType.FILL_BLANK,
            "question_text": f"Điền từ thích hợp vào chỗ trống:",
            "correct_answer": word,
            "options": None,  # Fill blank không có options cố định
            "context_sentence": context_sentence,
            "explanation": f"Từ đúng là '{word}'. {example_sentence}",
            "confusion_pair_group": confusion_group,
        }
        
        return question_data
    
    def get_question_type(self) -> QuestionType:
        """Trả về FILL_BLANK."""
        return QuestionType.FILL_BLANK
