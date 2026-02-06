"""
Enum types cho vocabulary learning system.
"""
from enum import Enum


class UserRole(str, Enum):
    """Role của user trong hệ thống."""
    ADMIN = "ADMIN"
    USER = "USER"


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
    GROQ = "groq"


class WordType(str, Enum):
    """Phân loại từ vựng (đơn giản hóa)."""
    FUNCTION_WORD = "function_word"
    CONTENT_WORD = "content_word"


class MeaningSource(str, Enum):
    """Nguồn gốc của definition."""
    MANUAL = "manual"                  # User nhập trực tiếp
    DICTIONARY_API = "dictionary_api"  # Từ Free Dictionary API
    AUTO_TRANSLATE = "auto_translate"  # Từ LibreTranslate fallback


class QuestionType(str, Enum):
    """Loại câu hỏi trong review session."""
    MEANING_INPUT = "meaning_input"          # Hiện nghĩa → nhập từ (Content Word)
    FILL_BLANK = "fill_blank"                # Điền từ vào chỗ trống (Function Word)
    MULTIPLE_CHOICE = "multiple_choice"      # Chọn đáp án đúng (Function Word)
    ERROR_DETECTION = "error_detection"      # Tìm và sửa lỗi trong câu


class QuestionDifficulty(str, Enum):
    """Mức độ khó của câu hỏi."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
