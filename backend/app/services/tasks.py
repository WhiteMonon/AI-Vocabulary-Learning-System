"""
Background tasks cho vocabulary system.
"""
from sqlmodel import Session
from app.db.session import engine
from app.services.sentence_generator import SentenceGeneratorService
from app.services.tts_service import TTSService
from app.services.question_pregenerator_service import QuestionPreGeneratorService
from app.core.logging import get_logger

logger = get_logger(__name__)


async def generate_example_sentence_task(vocab_id: int):
    """
    Background task để generate example sentence cho vocabulary.
    Chạy sau khi vocabulary được tạo thành công.
    
    Args:
        vocab_id: ID của vocabulary cần generate context
    """
    # Tạo session riêng cho background task
    with Session(engine) as db:
        try:
            service = SentenceGeneratorService(db)
            await service.generate_and_save(vocab_id)
        except Exception as e:
            logger.error(f"Background task failed for vocab {vocab_id}: {e}")


async def generate_audio_task(vocab_id: int):
    """
    Background task để generate audio cho vocabulary (dictation).
    Chạy sau khi vocabulary được tạo thành công.
    
    Args:
        vocab_id: ID của vocabulary cần generate audio
    """
    with Session(engine) as db:
        try:
            service = TTSService(db)
            await service.generate_audio_for_vocab_id(vocab_id)
        except Exception as e:
            logger.error(f"Audio generation failed for vocab {vocab_id}: {e}")


async def pre_generate_questions_task(vocab_id: int):
    """
    Background task để pre-generate questions cho vocabulary.
    Chạy sau khi vocabulary được tạo thành công.
    
    Args:
        vocab_id: ID của vocabulary cần pre-generate questions
    """
    with Session(engine) as db:
        try:
            service = QuestionPreGeneratorService(db)
            await service.pre_generate_for_vocab_id(vocab_id)
        except Exception as e:
            logger.error(f"Question pre-generation failed for vocab {vocab_id}: {e}")


