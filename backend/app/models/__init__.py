"""
Models module - SQLModel models cho vocabulary learning system.
"""
from app.models.enums import (
    UserRole, DifficultyLevel, ReviewQuality, PracticeType,
    WordType, MeaningSource
)
from app.models.user import User
from app.models.vocabulary import Vocabulary
from app.models.vocabulary_meaning import VocabularyMeaning
from app.models.dictionary_cache import DictionaryCache
from app.models.review_history import ReviewHistory
from app.models.ai_practice_log import AIPracticeLog

__all__ = [
    # Enums
    "UserRole",
    "DifficultyLevel",
    "ReviewQuality",
    "PracticeType",
    "WordType",
    "MeaningSource",
    # Models
    "User",
    "Vocabulary",
    "VocabularyMeaning",
    "DictionaryCache",
    "ReviewHistory",
    "AIPracticeLog",
]
