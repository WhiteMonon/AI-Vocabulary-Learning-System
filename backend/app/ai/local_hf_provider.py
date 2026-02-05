from app.ai.base import AIProvider
from app.ai.schemas import AIQuestion, AIEvaluation
from app.models.vocabulary import Vocabulary
from app.models.enums import PracticeType
from app.core.logging import get_logger

logger = get_logger(__name__)

class LocalHFProvider(AIProvider):
    """Provider cho Local HuggingFace models."""
    def __init__(self, model_path: str = "models/llama-2-7b"):
        # Giả định dùng thư viện như transformers hoặc llama-cpp-python
        self.model_path = model_path
        logger.info(f"Loading local model from {model_path}")

    async def generate_question(
        self, 
        vocab: Vocabulary, 
        practice_type: PracticeType = PracticeType.MULTIPLE_CHOICE
    ) -> AIQuestion:
        # Logic gọi model local
        pass

    async def evaluate_answer(self, question: AIQuestion, answer: str) -> AIEvaluation:
        # Logic gọi model local
        pass
