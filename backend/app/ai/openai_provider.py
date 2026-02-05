import json
from openai import AsyncOpenAI
from app.ai.base import AIProvider
from app.ai.schemas import AIQuestion, AIEvaluation
from app.ai import prompts
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
        if practice_type == PracticeType.MULTIPLE_CHOICE:
            prompt = prompts.MULTIPLE_CHOICE_GEN.format(
                word=vocab.word, 
                definition=vocab.definition
            )
        elif practice_type == PracticeType.FILL_BLANK:
            prompt = prompts.FILL_BLANK_GEN.format(
                word=vocab.word, 
                definition=vocab.definition
            )
        else:
            # Fallback hoặc các loại khác sau này
            prompt = f"Tạo câu hỏi {practice_type.value} cho từ {vocab.word}"
        
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
        prompt = prompts.GRAMMAR_EVAL.format(
            question=question.question_text,
            expected=question.correct_answer,
            answer=answer
        )
        
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
