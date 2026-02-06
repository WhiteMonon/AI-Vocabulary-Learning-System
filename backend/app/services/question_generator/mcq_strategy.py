"""
Strategy cho Function Word - Multiple Choice Question.
Hiện câu với context → User chọn từ đúng.
"""
import random
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy


# Confusion pairs cho prepositions (giống Fill Blank)
PREPOSITION_CONFUSION_GROUPS = {
    "at": ["in", "on", "to"],
    "in": ["at", "on", "into"],
    "on": ["at", "in", "onto"],
    "for": ["since", "from", "to"],
    "since": ["for", "from"],
    "to": ["for", "at", "into"],
}


class MCQStrategy(QuestionGeneratorStrategy):
    """
    Strategy cho Function Words - Multiple Choice.
    Generate câu hỏi với context sentence và options.
    """
    
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate MCQ question với intelligent distractors.
        
        Args:
            vocabulary: Function Word cần generate câu hỏi
            difficulty: Mức độ khó
            distractors: Danh sách vocabularies khác
            
        Returns:
            Question data snapshot
        """
        word = vocabulary.word
        
        # Lấy example sentence từ VocabularyContext (thay vì từ meanings)
        example_sentence = None
        if vocabulary.contexts:
            # Lấy context đầu tiên (hoặc random nếu muốn đa dạng)
            example_sentence = vocabulary.contexts[0].sentence
        
        # Fallback: nếu không có context, delegate sang MeaningQuestionStrategy
        if not example_sentence:
            from app.services.question_generator.meaning_strategy import MeaningQuestionStrategy
            meaning_strategy = MeaningQuestionStrategy()
            return meaning_strategy.generate(vocabulary, difficulty, distractors)
        
        # Tạo context sentence với blank
        context_sentence = example_sentence.replace(word, "___")
        
        # Generate distractors (ưu tiên confusion pairs)
        options = [word]
        
        # Ưu tiên confusion pairs
        if word in PREPOSITION_CONFUSION_GROUPS:
            confusion_words = PREPOSITION_CONFUSION_GROUPS[word]
            options.extend(confusion_words[:3])  # Lấy tối đa 3 confusion words
        else:
            # Fallback: lấy từ distractors list
            distractor_words = [v.word for v in distractors if v.word != word]
            options.extend(random.sample(distractor_words, min(3, len(distractor_words))))
        
        # Đảm bảo có đủ 4 options
        while len(options) < 4:
            options.append("other")
        
        # Shuffle options
        random.shuffle(options)
        
        # Xác định confusion group
        confusion_group = None
        if word in PREPOSITION_CONFUSION_GROUPS:
            confusion_group = f"preposition_{word}"
        
        question_data = {
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "question_text": context_sentence,
            "correct_answer": word,
            "options": options,
            "context_sentence": context_sentence,
            "explanation": f"Từ đúng là '{word}'. {example_sentence}",
            "confusion_pair_group": confusion_group,
        }
        
        return question_data
    
    def get_question_type(self) -> QuestionType:
        """Trả về MULTIPLE_CHOICE."""
        return QuestionType.MULTIPLE_CHOICE
