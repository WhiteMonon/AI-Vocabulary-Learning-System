import json
import httpx
from app.ai.base import AIProvider
from app.ai.schemas import AIQuestion, AIEvaluation
from app.models.vocabulary import Vocabulary
from app.models.enums import PracticeType
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class GroqProvider(AIProvider):
    def __init__(self, api_key: str = settings.GROQ_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-8b-8192"

    async def generate_question(
        self, 
        vocab: Vocabulary, 
        practice_type: PracticeType = PracticeType.MULTIPLE_CHOICE
    ) -> AIQuestion:
        prompt = f"Tạo câu hỏi {practice_type.value} cho từ '{vocab.word}'... (JSON format)"
        # Triển khai tương tự OpenAI nhưng dùng Groq API qua HTTP hoặc SDK
        # Ở đây dùng mẫu gọi qua httpx cho đơn giản minh họa
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()["choices"][0]["message"]["content"]
                return AIQuestion(**json.loads(data))
            except Exception as e:
                logger.error(f"Groq generate_question error: {str(e)}")
                raise

    async def evaluate_answer(self, question: AIQuestion, answer: str) -> AIEvaluation:
        # Tương tự như OpenAI
        pass
