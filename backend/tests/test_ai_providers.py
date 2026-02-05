import pytest
from unittest.mock import MagicMock, patch
from app.ai.factory import AIFactory
from app.ai.openai_provider import OpenAIProvider
from app.models.enums import AIProviderName, PracticeType
from app.models.vocabulary import Vocabulary
from app.ai.schemas import AIQuestion

def test_ai_factory_get_provider():
    provider = AIFactory.get_provider(AIProviderName.OPENAI)
    assert isinstance(provider, OpenAIProvider)

def test_ai_factory_invalid_provider():
    with pytest.raises(ValueError):
        AIFactory.get_provider("invalid_provider")

@pytest.mark.asyncio
async def test_openai_provider_generate_question():
    mock_vocab = MagicMock(spec=Vocabulary)
    mock_vocab.word = "test"
    mock_vocab.definition = "a trial"
    
    with patch("app.ai.openai_provider.AsyncOpenAI") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.chat.completions.create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content='{"question_text": "What is a test?", "correct_answer": "a trial", "practice_type": "multiple_choice"}'
                    )
                )
            ]
        )
        
        provider = OpenAIProvider(api_key="fake")
        question = await provider.generate_question(mock_vocab, PracticeType.MULTIPLE_CHOICE)
        
        assert isinstance(question, AIQuestion)
        assert question.question_text == "What is a test?"
