"""
Models module - SQLModel models cho vocabulary learning system.
"""
from app.models.user import User
from app.models.vocabulary import Vocabulary
from app.models.vocabulary_meaning import VocabularyMeaning
from app.models.vocabulary_context import VocabularyContext
from app.models.vocabulary_audio import VocabularyAudio
from app.models.review_history import ReviewHistory
from app.models.ai_practice_log import AIPracticeLog
from app.models.dictionary_cache import DictionaryCache
from app.models.review_session import ReviewSession
from app.models.generated_question import GeneratedQuestion
from app.models.enums import (
    UserRole,
    DifficultyLevel,
    ReviewQuality,
    PracticeType,
    AIProviderName,
    WordType,
    MeaningSource,
    QuestionType,
    QuestionDifficulty,
)

__all__ = [
    "User",
    "Vocabulary",
    "VocabularyMeaning",
    "VocabularyContext",
    "VocabularyAudio",
    "ReviewHistory",
    "AIPracticeLog",
    "DictionaryCache",
    "ReviewSession",
    "GeneratedQuestion",
    "UserRole",
    "DifficultyLevel",
    "ReviewQuality",
    "PracticeType",
    "AIProviderName",
    "WordType",
    "MeaningSource",
    "QuestionType",
    "QuestionDifficulty",
]

