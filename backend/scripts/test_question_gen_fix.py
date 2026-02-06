"""
Script để test fix cho question generation logic.
Verify rằng khi vocabulary không có example_sentence, system sẽ fallback sang MeaningQuestionStrategy.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.vocabulary import Vocabulary
from app.models.vocabulary_meaning import VocabularyMeaning
from app.models.enums import WordType, QuestionType, QuestionDifficulty
from app.services.question_generator.mcq_strategy import MCQStrategy
from app.services.question_generator.fill_blank_strategy import FillBlankStrategy


def test_mcq_fallback():
    """Test MCQStrategy fallback khi không có example sentence."""
    print("=" * 60)
    print("TEST 1: MCQStrategy Fallback")
    print("=" * 60)
    
    # Tạo vocabulary KHÔNG có example_sentence
    vocab = Vocabulary(
        id=1,
        user_id=1,
        word="at",
        word_type=WordType.FUNCTION_WORD,
        repetitions=0
    )
    
    # Tạo meaning KHÔNG có example_sentence
    meaning = VocabularyMeaning(
        id=1,
        vocabulary_id=1,
        definition="Preposition indicating location or time",
        example_sentence=None  # KHÔNG có example
    )
    vocab.meanings = [meaning]
    
    # Generate question
    strategy = MCQStrategy()
    question_data = strategy.generate(vocab, QuestionDifficulty.EASY, [])
    
    # Verify
    print(f"Question Type: {question_data['question_type']}")
    print(f"Question Text: {question_data['question_text']}")
    print(f"Correct Answer: {question_data['correct_answer']}")
    print(f"Options: {question_data.get('options')}")
    
    # Assert: nên là MEANING_INPUT vì không có example
    assert question_data['question_type'] == QuestionType.MEANING_INPUT, \
        f"Expected MEANING_INPUT, got {question_data['question_type']}"
    assert question_data['correct_answer'] == "at", \
        f"Expected correct_answer='at', got {question_data['correct_answer']}"
    
    print("✅ MCQStrategy fallback works correctly!")
    print()


def test_fill_blank_fallback():
    """Test FillBlankStrategy fallback khi không có example sentence."""
    print("=" * 60)
    print("TEST 2: FillBlankStrategy Fallback")
    print("=" * 60)
    
    # Tạo vocabulary KHÔNG có example_sentence
    vocab = Vocabulary(
        id=2,
        user_id=1,
        word="in",
        word_type=WordType.FUNCTION_WORD,
        repetitions=1
    )
    
    # Tạo meaning KHÔNG có example_sentence
    meaning = VocabularyMeaning(
        id=2,
        vocabulary_id=2,
        definition="Preposition indicating location inside",
        example_sentence=None  # KHÔNG có example
    )
    vocab.meanings = [meaning]
    
    # Generate question
    strategy = FillBlankStrategy()
    question_data = strategy.generate(vocab, QuestionDifficulty.MEDIUM, [])
    
    # Verify
    print(f"Question Type: {question_data['question_type']}")
    print(f"Question Text: {question_data['question_text']}")
    print(f"Correct Answer: {question_data['correct_answer']}")
    print(f"Context Sentence: {question_data.get('context_sentence')}")
    
    # Assert: nên là MEANING_INPUT vì không có example
    assert question_data['question_type'] == QuestionType.MEANING_INPUT, \
        f"Expected MEANING_INPUT, got {question_data['question_type']}"
    assert question_data['correct_answer'] == "in", \
        f"Expected correct_answer='in', got {question_data['correct_answer']}"
    
    print("✅ FillBlankStrategy fallback works correctly!")
    print()


def test_mcq_with_example():
    """Test MCQStrategy khi CÓ example sentence (normal flow)."""
    print("=" * 60)
    print("TEST 3: MCQStrategy With Example (Normal Flow)")
    print("=" * 60)
    
    # Tạo vocabulary CÓ example_sentence
    vocab = Vocabulary(
        id=3,
        user_id=1,
        word="at",
        word_type=WordType.FUNCTION_WORD,
        repetitions=0
    )
    
    # Tạo meaning CÓ example_sentence
    meaning = VocabularyMeaning(
        id=3,
        vocabulary_id=3,
        definition="Preposition indicating location or time",
        example_sentence="She is good at math."  # CÓ example
    )
    vocab.meanings = [meaning]
    
    # Generate question
    strategy = MCQStrategy()
    question_data = strategy.generate(vocab, QuestionDifficulty.EASY, [])
    
    # Verify
    print(f"Question Type: {question_data['question_type']}")
    print(f"Question Text: {question_data['question_text']}")
    print(f"Correct Answer: {question_data['correct_answer']}")
    print(f"Options: {question_data.get('options')}")
    
    # Assert: nên là MULTIPLE_CHOICE vì có example
    assert question_data['question_type'] == QuestionType.MULTIPLE_CHOICE, \
        f"Expected MULTIPLE_CHOICE, got {question_data['question_type']}"
    assert question_data['correct_answer'] == "at", \
        f"Expected correct_answer='at', got {question_data['correct_answer']}"
    assert "___" in question_data['question_text'], \
        "Expected blank '___' in question text"
    assert "at" in question_data['options'], \
        "Expected 'at' in options"
    
    print("✅ MCQStrategy normal flow works correctly!")
    print()


if __name__ == "__main__":
    try:
        test_mcq_fallback()
        test_fill_blank_fallback()
        test_mcq_with_example()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
