"""
Script để test fix cho empty question UI issue.
Verify rằng khi vocabulary có definition rỗng, system sẽ fallback sang text "Từ vựng: {word}".
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.vocabulary import Vocabulary
from app.models.vocabulary_meaning import VocabularyMeaning
from app.models.enums import WordType, QuestionType, QuestionDifficulty
from app.services.question_generator.meaning_strategy import MeaningQuestionStrategy

def test_empty_definition_fallback():
    """Test MeaningQuestionStrategy fallback khi definition rỗng."""
    print("=" * 60)
    print("TEST: MeaningQuestionStrategy Empty Definition Fallback")
    print("=" * 60)
    
    # Tạo vocabulary
    vocab = Vocabulary(
        id=1,
        user_id=1,
        word="test_word",
        word_type=WordType.CONTENT_WORD,
        repetitions=0
    )
    
    # Case 1: No meanings
    print("Case 1: No meanings")
    vocab.meanings = []
    
    strategy = MeaningQuestionStrategy()
    question_data = strategy.generate(vocab, QuestionDifficulty.EASY, [])
    
    print(f"Question Text: '{question_data['question_text']}'")
    assert question_data['question_text'] == "Từ vựng: test_word", \
        f"Expected 'Từ vựng: test_word', got '{question_data['question_text']}'"
    print("✅ Fallback works for no meanings")
    
    # Case 2: Empty definition
    print("\nCase 2: Empty definition string")
    meaning = VocabularyMeaning(
        id=1,
        vocabulary_id=1,
        definition="", # Empty string
        example_sentence=None
    )
    vocab.meanings = [meaning]
    
    question_data = strategy.generate(vocab, QuestionDifficulty.EASY, [])
    
    print(f"Question Text: '{question_data['question_text']}'")
    assert question_data['question_text'] == "Từ vựng: test_word", \
        f"Expected 'Từ vựng: test_word', got '{question_data['question_text']}'"
    print("✅ Fallback works for empty definition string")
    
    # Case 3: None definition
    print("\nCase 3: None definition")
    meaning = VocabularyMeaning(
        id=1,
        vocabulary_id=1,
        definition=None, # None
        example_sentence=None
    )
    vocab.meanings = [meaning]
    
    question_data = strategy.generate(vocab, QuestionDifficulty.EASY, [])
    
    print(f"Question Text: '{question_data['question_text']}'")
    assert question_data['question_text'] == "Từ vựng: test_word", \
        f"Expected 'Từ vựng: test_word', got '{question_data['question_text']}'"
    print("✅ Fallback works for None definition")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_empty_definition_fallback()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
