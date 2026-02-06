"""
Factory để chọn strategy phù hợp cho question generation.
"""
import random
from typing import List
from app.models.vocabulary import Vocabulary
from app.models.enums import WordType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy
from app.services.question_generator.meaning_strategy import MeaningQuestionStrategy
from app.services.question_generator.fill_blank_strategy import FillBlankStrategy
from app.services.question_generator.mcq_strategy import MCQStrategy


class QuestionGeneratorFactory:
    """
    Factory để chọn strategy phù hợp dựa trên word_type và context.
    """
    
    @staticmethod
    def get_strategy(
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty
    ) -> QuestionGeneratorStrategy:
        """
        Chọn strategy phù hợp cho vocabulary.
        
        Args:
            vocabulary: Vocabulary cần generate câu hỏi
            difficulty: Mức độ khó
            
        Returns:
            QuestionGeneratorStrategy phù hợp
        """
        # Content Word → Meaning Input
        if vocabulary.word_type == WordType.CONTENT_WORD:
            return MeaningQuestionStrategy()
        
        # Function Word → Fill Blank hoặc MCQ
        # Ưu tiên MCQ cho new words (dễ hơn)
        # Ưu tiên Fill Blank cho words đã học (khó hơn)
        is_new = vocabulary.repetitions == 0
        
        if is_new:
            # New word: 70% MCQ, 30% Fill Blank
            return MCQStrategy() if random.random() < 0.7 else FillBlankStrategy()
        else:
            # Learned word: 40% MCQ, 60% Fill Blank
            return MCQStrategy() if random.random() < 0.4 else FillBlankStrategy()
