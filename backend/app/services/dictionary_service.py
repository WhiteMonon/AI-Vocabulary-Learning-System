"""
DictionaryService - Service để fetch definitions từ external APIs.
Hỗ trợ Free Dictionary API và LibreTranslate fallback.
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

from sqlmodel import Session, select

from app.models.dictionary_cache import DictionaryCache
from app.models.enums import MeaningSource
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class DictionaryService:
    """
    Service để fetch definitions từ external APIs.
    
    Fallback chain:
    1. Check cache trong DB
    2. Free Dictionary API (https://dictionaryapi.dev/)
    3. LibreTranslate fallback
    """
    
    # API endpoints
    DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    LIBRETRANSLATE_API_URL = getattr(settings, 'LIBRETRANSLATE_URL', 'https://libretranslate.com/translate')
    
    # Cache TTL
    CACHE_TTL_DAYS = 30
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 10  # requests per second
    
    def __init__(self, session: Session):
        """
        Initialize dictionary service.
        
        Args:
            session: Database session
        """
        self.session = session
        self._http_client: Optional[httpx.AsyncClient] = None
    
    @property
    def http_client(self) -> httpx.AsyncClient:
        """Lazy-load HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=10.0)
        return self._http_client
    
    async def close(self):
        """Close HTTP client khi không cần nữa."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    def _normalize_word(self, word: str) -> str:
        """Normalize word: lowercase, trim, remove duplicate spaces."""
        return " ".join(word.strip().lower().split())
    
    def _get_from_cache(self, word: str) -> Optional[DictionaryCache]:
        """
        Lấy definition từ cache.
        
        Args:
            word: Từ cần tra cứu (đã normalized)
            
        Returns:
            DictionaryCache nếu tìm thấy và chưa hết hạn, None otherwise
        """
        normalized = self._normalize_word(word)
        
        query = select(DictionaryCache).where(
            DictionaryCache.word == normalized,
            DictionaryCache.expires_at > datetime.utcnow()
        )
        
        result = self.session.exec(query).first()
        
        if result:
            logger.debug(f"Cache hit for word: {normalized}")
        
        return result
    
    def _save_to_cache(self, word: str, definition: str, source: MeaningSource) -> DictionaryCache:
        """
        Lưu definition vào cache.
        
        Args:
            word: Từ (sẽ được normalized)
            definition: Definition
            source: Nguồn của definition
            
        Returns:
            DictionaryCache entry đã tạo
        """
        normalized = self._normalize_word(word)
        
        # Check xem đã có entry chưa
        existing = self.session.exec(
            select(DictionaryCache).where(DictionaryCache.word == normalized)
        ).first()
        
        if existing:
            # Update existing entry
            existing.definition = definition
            existing.source = source
            existing.fetched_at = datetime.utcnow()
            existing.expires_at = datetime.utcnow() + timedelta(days=self.CACHE_TTL_DAYS)
            self.session.add(existing)
            self.session.commit()
            return existing
        
        # Create new entry
        cache_entry = DictionaryCache.create_with_ttl(
            word=normalized,
            definition=definition,
            source=source,
            ttl_days=self.CACHE_TTL_DAYS
        )
        
        self.session.add(cache_entry)
        self.session.commit()
        self.session.refresh(cache_entry)
        
        logger.info(f"Cached definition for: {normalized} from {source.value}")
        return cache_entry
    
    async def _fetch_dictionary_api(self, word: str) -> Optional[str]:
        """
        Fetch definition từ Free Dictionary API.
        
        Args:
            word: Từ cần tra cứu
            
        Returns:
            Definition string nếu thành công, None otherwise
        """
        normalized = self._normalize_word(word)
        url = self.DICTIONARY_API_URL.format(word=normalized)
        
        try:
            response = await self.http_client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response - lấy definition đầu tiên
                if data and isinstance(data, list) and len(data) > 0:
                    meanings = data[0].get("meanings", [])
                    if meanings:
                        definitions = meanings[0].get("definitions", [])
                        if definitions:
                            definition = definitions[0].get("definition", "")
                            if definition:
                                logger.info(f"Dictionary API success for: {normalized}")
                                return definition
            
            elif response.status_code == 404:
                logger.debug(f"Dictionary API: word not found - {normalized}")
            else:
                logger.warning(f"Dictionary API error: {response.status_code} for {normalized}")
                
        except httpx.TimeoutException:
            logger.warning(f"Dictionary API timeout for: {normalized}")
        except Exception as e:
            logger.error(f"Dictionary API error for {normalized}: {str(e)}")
        
        return None
    
    async def _fetch_translation(self, word: str) -> Optional[str]:
        """
        Fallback: Fetch translation/definition từ LibreTranslate.
        
        Args:
            word: Từ cần tra cứu
            
        Returns:
            Translation string nếu thành công, None otherwise
        """
        normalized = self._normalize_word(word)
        
        try:
            # LibreTranslate API call
            payload = {
                "q": normalized,
                "source": "en",
                "target": "vi",  # Translate to Vietnamese
                "format": "text"
            }
            
            response = await self.http_client.post(
                self.LIBRETRANSLATE_API_URL,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                translation = data.get("translatedText", "")
                
                if translation and translation.lower() != normalized:
                    logger.info(f"LibreTranslate success for: {normalized}")
                    return translation
            else:
                logger.warning(f"LibreTranslate error: {response.status_code}")
                
        except httpx.TimeoutException:
            logger.warning(f"LibreTranslate timeout for: {normalized}")
        except Exception as e:
            logger.error(f"LibreTranslate error for {normalized}: {str(e)}")
        
        return None
    
    async def get_definition(self, word: str) -> Tuple[Optional[str], Optional[MeaningSource]]:
        """
        Fetch definition với fallback chain.
        
        Chain: Cache → Dictionary API → LibreTranslate
        
        Args:
            word: Từ cần tra cứu
            
        Returns:
            Tuple (definition, source) hoặc (None, None) nếu không tìm thấy
        """
        normalized = self._normalize_word(word)
        
        # 1. Check cache
        cached = self._get_from_cache(normalized)
        if cached:
            return cached.definition, cached.source
        
        # 2. Try Dictionary API
        definition = await self._fetch_dictionary_api(normalized)
        if definition:
            self._save_to_cache(normalized, definition, MeaningSource.DICTIONARY_API)
            return definition, MeaningSource.DICTIONARY_API
        
        # 3. Fallback: LibreTranslate
        definition = await self._fetch_translation(normalized)
        if definition:
            self._save_to_cache(normalized, definition, MeaningSource.AUTO_TRANSLATE)
            return definition, MeaningSource.AUTO_TRANSLATE
        
        logger.warning(f"No definition found for: {normalized}")
        return None, None
    
    async def batch_get_definitions(
        self,
        words: List[str],
        rate_limit: int = None
    ) -> Dict[str, Tuple[Optional[str], Optional[MeaningSource]]]:
        """
        Batch fetch definitions với rate limiting.
        
        Args:
            words: Danh sách từ cần tra cứu
            rate_limit: Số requests tối đa mỗi giây
            
        Returns:
            Dict mapping word → (definition, source)
        """
        rate_limit = rate_limit or self.DEFAULT_RATE_LIMIT
        results: Dict[str, Tuple[Optional[str], Optional[MeaningSource]]] = {}
        
        # Normalize tất cả words
        normalized_words = [self._normalize_word(w) for w in words]
        unique_words = list(set(normalized_words))
        
        logger.info(f"Batch fetching definitions for {len(unique_words)} unique words")
        
        # Process với rate limiting
        for i, word in enumerate(unique_words):
            results[word] = await self.get_definition(word)
            
            # Rate limiting: sleep sau mỗi batch
            if (i + 1) % rate_limit == 0 and i < len(unique_words) - 1:
                await asyncio.sleep(1)
        
        return results
    
    def cleanup_expired_cache(self) -> int:
        """
        Xóa các cache entries đã hết hạn.
        
        Returns:
            Số lượng entries đã xóa
        """
        expired = self.session.exec(
            select(DictionaryCache).where(
                DictionaryCache.expires_at <= datetime.utcnow()
            )
        ).all()
        
        count = len(expired)
        for entry in expired:
            self.session.delete(entry)
        
        if count > 0:
            self.session.commit()
            logger.info(f"Cleaned up {count} expired cache entries")
        
        return count
