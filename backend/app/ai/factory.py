from typing import Dict, Type
from app.ai.base import AIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.groq_provider import GroqProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.local_hf_provider import LocalHFProvider
from app.models.enums import AIProviderName
from app.core.config import settings

class AIFactory:
    """Factory class để khởi tạo AI Provider."""
    
    _providers: Dict[str, Type[AIProvider]] = {
        AIProviderName.OPENAI: OpenAIProvider,
        AIProviderName.GROQ: GroqProvider,
        AIProviderName.GEMINI: GeminiProvider,
        AIProviderName.LOCAL_HF: LocalHFProvider
    }

    @classmethod
    def get_provider(cls, provider_name: str = None) -> AIProvider:
        """
        Lấy instance của provider dựa trên tên.
        Nếu không truyền tên, lấy provider mặc định từ settings.
        """
        name = provider_name or settings.DEFAULT_AI_PROVIDER
        provider_class = cls._providers.get(name)
        
        if not provider_class:
            raise ValueError(f"AI Provider '{name}' không được hỗ trợ.")
            
        return provider_class()

def get_ai_provider(provider_name: str = None) -> AIProvider:
    """Helper function để lấy AI provider."""
    return AIFactory.get_provider(provider_name)
