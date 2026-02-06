"""
Enum types cho vocabulary learning system.
"""
from enum import Enum


class UserRole(str, Enum):
    """Role của user trong hệ thống."""
    ADMIN = "admin"
    USER = "user"


class DifficultyLevel(str, Enum):
    """Mức độ khó của vocabulary."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ReviewQuality(int, Enum):
    """
    Chất lượng review theo SM-2 algorithm.
    0: Again (hoàn toàn quên)
    1: Hard (nhớ khó khăn)
    2: Good (nhớ tốt)
    3: Easy (nhớ rất dễ)
    """
    AGAIN = 0
    HARD = 1
    GOOD = 2
    EASY = 3


class PracticeType(str, Enum):
    """Loại bài tập AI practice."""
    FLASHCARD = "flashcard"
    FILL_BLANK = "fill_blank"
    MULTIPLE_CHOICE = "multiple_choice"
    SENTENCE_GENERATION = "sentence_generation"


class AIProviderName(str, Enum):
    """Tên các AI providers được hỗ trợ."""
    OPENAI = "openai"
    GROQ = "groq"
    GEMINI = "gemini"
    LOCAL_HF = "local"


class WordType(str, Enum):
    """Phân loại từ vựng: Function Words vs Content Words."""
    FUNCTION_WORD = "function_word"  # the, a, is, are, in, on...
    CONTENT_WORD = "content_word"    # nouns, verbs, adjectives, adverbs


class MeaningSource(str, Enum):
    """Nguồn gốc của definition."""
    MANUAL = "manual"                  # User nhập trực tiếp
    DICTIONARY_API = "dictionary_api"  # Từ Free Dictionary API
    AUTO_TRANSLATE = "auto_translate"  # Từ LibreTranslate fallback
