import google.generativeai as genai
from app.ai.base import AIProvider
from app.ai.schemas import AIQuestion, AIEvaluation
from app.models.vocabulary import Vocabulary
from app.models.enums import PracticeType
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_question(
        self, 
        vocab: Vocabulary, 
        practice_type: PracticeType = PracticeType.MULTIPLE_CHOICE
    ) -> AIQuestion:
        # Implement Gemini specific logic
        pass

    async def evaluate_answer(self, question: AIQuestion, answer: str) -> AIEvaluation:
        # Implement Gemini specific logic
        pass
