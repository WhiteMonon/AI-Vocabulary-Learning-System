"""
Test script để verify Phase 2 implementation.
Kiểm tra:
1. Vocabulary creation triggers background sentence generation
2. Question generators use VocabularyContext correctly
3. Migration data integrity
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlmodel import Session, select
from app.db.session import engine
from app.models.vocabulary import Vocabulary
from app.models.vocabulary_context import VocabularyContext
from app.models.vocabulary_meaning import VocabularyMeaning
from app.services.sentence_generator import SentenceGeneratorService
from app.services.question_generator.factory import QuestionGeneratorFactory
from app.models.enums import QuestionDifficulty, WordType


async def test_phase_2():
    """Test toàn bộ Phase 2 flow."""
    
    print("=" * 60)
    print("PHASE 2 VERIFICATION TEST")
    print("=" * 60)
    
    with Session(engine) as db:
        # Test 1: Check migration - VocabularyContext table exists
        print("\n[TEST 1] Checking VocabularyContext table...")
        contexts = db.exec(select(VocabularyContext)).all()
        print(f"✓ Found {len(contexts)} contexts in database")
        
        # Test 2: Check that VocabularyMeaning no longer has example_sentence
        print("\n[TEST 2] Checking VocabularyMeaning schema...")
        meaning = db.exec(select(VocabularyMeaning).limit(1)).first()
        if meaning:
            # Try to access example_sentence (should fail)
            try:
                _ = meaning.example_sentence
                print("✗ FAILED: example_sentence field still exists!")
            except AttributeError:
                print("✓ example_sentence field removed successfully")
        
        # Test 3: Test SentenceGeneratorService
        print("\n[TEST 3] Testing SentenceGeneratorService...")
        vocab = db.exec(
            select(Vocabulary)
            .where(Vocabulary.word_type == WordType.FUNCTION_WORD)
            .limit(1)
        ).first()
        
        if vocab:
            print(f"  Testing with vocab: '{vocab.word}'")
            service = SentenceGeneratorService(db)
            
            # Check if context already exists
            if vocab.contexts:
                print(f"  ✓ Vocab already has {len(vocab.contexts)} context(s)")
                print(f"    Example: {vocab.contexts[0].sentence}")
            else:
                print("  No context found, generating...")
                context = await service.generate_and_save(vocab.id)
                if context:
                    print(f"  ✓ Generated context: {context.sentence}")
                else:
                    print("  ⚠ Context generation skipped or failed")
        
        # Test 4: Test Question Generator with VocabularyContext
        print("\n[TEST 4] Testing Question Generator...")
        function_word = db.exec(
            select(Vocabulary)
            .where(Vocabulary.word_type == WordType.FUNCTION_WORD)
            .limit(1)
        ).first()
        
        if function_word:
            db.refresh(function_word)  # Reload with contexts
            print(f"  Testing with function word: '{function_word.word}'")
            print(f"  Contexts available: {len(function_word.contexts)}")
            
            strategy = QuestionGeneratorFactory.get_strategy(
                function_word,
                QuestionDifficulty.MEDIUM
            )
            
            question = strategy.generate(
                function_word,
                QuestionDifficulty.MEDIUM,
                []
            )
            
            print(f"  ✓ Generated question type: {question['question_type']}")
            print(f"    Question text: {question['question_text'][:80]}...")
        
        # Test 5: Check data migration integrity
        print("\n[TEST 5] Checking data migration integrity...")
        migrated_contexts = db.exec(
            select(VocabularyContext)
            .where(VocabularyContext.ai_provider == "migrated")
        ).all()
        print(f"  ✓ Found {len(migrated_contexts)} migrated contexts")
        if migrated_contexts:
            sample = migrated_contexts[0]
            print(f"    Sample: vocab_id={sample.vocabulary_id}, sentence='{sample.sentence[:50]}...'")
    
    print("\n" + "=" * 60)
    print("PHASE 2 VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_phase_2())
