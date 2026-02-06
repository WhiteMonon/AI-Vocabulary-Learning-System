"""
DictionaryService - Service để dịch từ vựng sử dụng Google Translate.
"""
from typing import Optional, Tuple
from sqlmodel import Session

from app.models.enums import MeaningSource
from app.core.logging import get_logger

logger = get_logger(__name__)


class DictionaryService:
    """
    Service để dịch từ vựng từ tiếng Anh sang tiếng Việt sử dụng Google Translate.
    """
    
    def __init__(self, session: Session):
        """
        Initialize dictionary service.
        
        Args:
            session: Database session (giữ để tương thích)
        """
        self.session = session
    
    async def translate_text(self, text: str, source_lang: str = "en", target_lang: str = "vi") -> Optional[str]:
        """
        Dịch văn bản sang tiếng Việt.
        
        Args:
            text: Văn bản cần dịch
            source_lang: Ngôn ngữ nguồn (mặc định: en)
            target_lang: Ngôn ngữ đích (mặc định: vi)
            
        Returns:
            Văn bản đã dịch hoặc None nếu thất bại
        """
        if not text or not text.strip():
            return None
        
        try:
            # Dùng deep_translator ổn định hơn googletrans
            from deep_translator import GoogleTranslator
            
            # GoogleTranslator là synchronous, chạy trong executor để không block event loop
            import asyncio
            import functools
            
            loop = asyncio.get_event_loop()
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Dùng run_in_executor để chạy sync function trong async context
            result = await loop.run_in_executor(
                None, 
                functools.partial(translator.translate, text)
            )
            
            if result:
                logger.info(f"Translated: '{text}' -> '{result}'")
                return result
            else:
                logger.warning(f"Translation failed for: '{text}'")
                return None
                
        except Exception as e:
            logger.error(f"Translation error for '{text}': {str(e)}")
            return None
    
    async def get_definition(self, word: str) -> Tuple[Optional[str], Optional[MeaningSource]]:
        """
        Lấy định nghĩa tiếng Việt của từ.
        
        Args:
            word: Từ cần tra cứu
            
        Returns:
            Tuple (definition, source) hoặc (None, None) nếu thất bại
        """
        definition = await self.translate_text(word.strip().lower())
        
        if definition:
            return definition, MeaningSource.AUTO_TRANSLATE
        
        return None, None
    
    def cleanup_expired_cache(self) -> int:
        """
        Không còn sử dụng cache - giữ method để tương thích.
        
        Returns:
            0
        """
        return 0

