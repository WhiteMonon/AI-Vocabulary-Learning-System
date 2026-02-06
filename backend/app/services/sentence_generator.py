"""
Sentence Generator Service - Background service để generate example sentences bằng AI.
"""
from typing import Optional
from sqlmodel import Session
from app.models.vocabulary import Vocabulary
from app.models.vocabulary_context import VocabularyContext
from app.ai.factory import get_ai_provider
from app.ai.prompts import EXAMPLE_SENTENCE_GEN
from app.core.logging import get_logger

logger = get_logger(__name__)


class SentenceGeneratorService:
    """
    Service để generate và lưu example sentences cho vocabulary.
    Chạy trong background task sau khi vocabulary được tạo.
    """
    
    def __init__(self, db: Session):
        """
        Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.ai_provider = get_ai_provider()
    
    async def generate_and_save(self, vocab_id: int) -> Optional[VocabularyContext]:
        """
        Generate example sentence cho vocabulary và lưu vào database.
        
        Args:
            vocab_id: ID của vocabulary
            
        Returns:
            VocabularyContext đã tạo, hoặc None nếu thất bại
        """
        try:
            # Lấy vocabulary từ DB
            vocab = self.db.get(Vocabulary, vocab_id)
            if not vocab:
                logger.warning(f"Vocabulary {vocab_id} not found")
                return None
            
            # Check nếu đã có context rồi thì skip
            if vocab.contexts:
                logger.debug(f"Vocabulary {vocab_id} already has context, skipping")
                return None
            
            # Lấy definition để làm context cho AI
            definition = ""
            if vocab.meanings:
                definition = vocab.meanings[0].definition
            
            # Build prompt
            prompt = EXAMPLE_SENTENCE_GEN.format(
                word=vocab.word,
                definition=definition,
                word_type=vocab.word_type.value
            )
            
            # Call AI to generate sentence
            logger.info(f"Generating example sentence for vocab '{vocab.word}' (ID: {vocab_id})")
            sentence = await self.ai_provider.generate_sentence(prompt)
            
            if not sentence or not sentence.strip():
                logger.warning(f"AI returned empty sentence for vocab {vocab_id}")
                return None
            
            # Save to database
            context = VocabularyContext(
                vocabulary_id=vocab_id,
                sentence=sentence.strip(),
                ai_provider=self.ai_provider.__class__.__name__.replace("Provider", "").lower()
            )
            
            self.db.add(context)
            self.db.commit()
            self.db.refresh(context)
            
            logger.info(f"Successfully generated context for vocab '{vocab.word}': {sentence[:50]}...")
            return context
            
        except Exception as e:
            logger.error(f"Failed to generate context for vocab {vocab_id}: {e}")
            self.db.rollback()
            return None
