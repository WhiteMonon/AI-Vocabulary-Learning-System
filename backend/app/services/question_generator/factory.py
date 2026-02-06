"""
Factory để chọn strategy phù hợp cho question generation.
"""
import random
from typing import List, Dict, Any
from app.models.vocabulary import Vocabulary
from app.models.enums import WordType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy
from app.services.question_generator.meaning_strategy import MeaningQuestionStrategy
from app.services.question_generator.usage_context_strategy import UsageContextStrategy
from app.services.question_generator.dictation_strategy import DictationStrategy
from app.services.question_generator.synonym_antonym_strategy import SynonymAntonymStrategy
from app.services.question_generator.definition_mcq_strategy import DefinitionMCQStrategy
from app.services.question_generator.fill_blank_strategy import FillBlankStrategy
from app.services.question_generator.mcq_strategy import MCQStrategy

# Content Word strategies với phân bố đều
CONTENT_WORD_STRATEGIES = [
    MeaningQuestionStrategy,       # 1. Word from Meaning (typing)
    DictationStrategy,             # 2. Dictation (audio)
    FillBlankStrategy,             # 3. Fill in the Blank (context)
    SynonymAntonymStrategy,        # 4. Synonym MCQ (word options)
    UsageContextStrategy,          # 5. Usage in Context MCQ
]


# Function Word strategies
FUNCTION_WORD_STRATEGIES = [
    MCQStrategy,
    FillBlankStrategy,
]


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
        # Content Word → Random từ 5 strategies
        if vocabulary.word_type == WordType.CONTENT_WORD:
            strategy_class = random.choice(CONTENT_WORD_STRATEGIES)
            return strategy_class()
        
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
    
    @staticmethod
    def generate_multiple_questions(
        vocabulary: Vocabulary,
        count: int,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> List[Dict[str, Any]]:
        """
        Generate nhiều câu hỏi cho 1 vocabulary, đảm bảo đa dạng types và context.
        """
        questions = []
        
        # 1. Prepare available contexts
        available_contexts = []
        if vocabulary.contexts:
            available_contexts = [c.sentence for c in vocabulary.contexts]
        
        # Helper to get a random context (or None to let strategy decide/fallback)
        def get_context_for_question():
            if available_contexts:
                return random.choice(available_contexts)
            return None

        if vocabulary.word_type == WordType.CONTENT_WORD:
            # Content Word: đảm bảo mỗi type xuất hiện ít nhất 1 lần nếu count >= 5
            strategies_to_use = []
            
            if count >= len(CONTENT_WORD_STRATEGIES):
                # Mỗi type 1 lần trước
                strategies_to_use = [s() for s in CONTENT_WORD_STRATEGIES]
                # Random thêm cho đủ count
                remaining = count - len(strategies_to_use)
                for _ in range(remaining):
                    strategies_to_use.append(random.choice(CONTENT_WORD_STRATEGIES)())
            else:
                # Ít hơn 5: random chọn nhưng ưu tiên không trùng lặp
                possible_strategies = list(CONTENT_WORD_STRATEGIES)
                random.shuffle(possible_strategies)
                strategies_to_use = [possible_strategies[i % len(possible_strategies)]() for i in range(count)]
            
            random.shuffle(strategies_to_use)
            
            for strategy in strategies_to_use:
                # Inject a random context into generation (if strategy supports it)
                # Note: Currently strategies extract context internally. 
                # We need to modifying strategies to accept context injection or 
                # randomness. For now, let's rely on strategies picking random contexts.
                question_data = strategy.generate(vocabulary, difficulty, distractors)
                questions.append(question_data)
        else:
            # Function Word: MCQ + Fill Blank
            for i in range(count):
                # Xen kẽ MCQ và Fill Blank
                if i % 2 == 0:
                    strategy = MCQStrategy()
                else:
                    strategy = FillBlankStrategy()
                question_data = strategy.generate(vocabulary, difficulty, distractors)
                questions.append(question_data)
        
        return questions

