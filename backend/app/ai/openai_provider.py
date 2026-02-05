import json
from openai import AsyncOpenAI
from app.ai.base import AIProvider
from app.ai.schemas import AIQuestion, AIEvaluation
from app.models.vocabulary import Vocabulary
from app.models.enums import PracticeType
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str = settings.OPENAI_API_KEY):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"

    async def generate_question(
        self, 
        vocab: Vocabulary, 
        practice_type: PracticeType = PracticeType.MULTIPLE_CHOICE
    ) -> AIQuestion:
        prompt = f"""
        Tạo một câu hỏi {practice_type.value} cho từ vựng sau:
        Từ: {vocab.word}
        Định nghĩa: {vocab.definition}
        
        Yêu cầu trả về định dạng JSON:
        {{
            "question_text": "nội dung câu hỏi",
            "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}} (nếu là trắc nghiệm),
            "correct_answer": "đáp án đúng",
            "explanation": "giải thích tại sao đáp án đó đúng",
            "practice_type": "{practice_type.value}"
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a helpful language teacher."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return AIQuestion(**data)
        except Exception as e:
            logger.error(f"OpenAI generate_question error: {str(e)}")
            raise

    async def evaluate_answer(self, question: AIQuestion, answer: str) -> AIEvaluation:
        prompt = f"""
        Câu hỏi: {question.question_text}
        Đáp án đúng: {question.correct_answer}
        Câu trả lời của người dùng: {answer}
        
        Hãy đánh giá câu trả lời này. Trả về định dạng JSON:
        {{
            "is_correct": true/false,
            "feedback": "nhận xét ngắn gọn",
            "score": 0.0 đến 1.0
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a helpful language teacher."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return AIEvaluation(**data)
        except Exception as e:
            logger.error(f"OpenAI evaluate_answer error: {str(e)}")
            raise
