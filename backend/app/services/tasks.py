"""
Background tasks cho vocabulary system.
"""
from sqlmodel import Session
from app.db.session import engine
from app.services.sentence_generator import SentenceGeneratorService
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
