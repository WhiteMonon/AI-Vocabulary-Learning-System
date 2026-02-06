"""
TTS Service - Text-to-Speech service sử dụng Edge-TTS.
Dùng để generate audio cho dictation questions.
"""
import os
import asyncio
from pathlib import Path
from typing import Optional, Tuple
from sqlmodel import Session

from app.core.logging import get_logger
from app.core.config import settings
from app.models.vocabulary import Vocabulary
from app.models.vocabulary_audio import VocabularyAudio

logger = get_logger(__name__)

# Thư mục lưu audio files
AUDIO_DIR = Path("static/audio")

# Voice options cho Edge-TTS
DEFAULT_VOICE = "en-US-AriaNeural"  # Giọng nữ Mỹ tự nhiên
DEFAULT_LANGUAGE = "en-US"


class TTSService:
    """
    Service để generate audio cho từ vựng sử dụng Edge-TTS.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_audio(
        self,
        vocabulary: Vocabulary,
        voice: str = DEFAULT_VOICE,
        language: str = DEFAULT_LANGUAGE
    ) -> Optional[VocabularyAudio]:
        """
        Generate audio file cho vocabulary và lưu vào database.
        
        Args:
            vocabulary: Vocabulary cần generate audio
            voice: Voice name từ Edge-TTS
            language: Language code
            
        Returns:
            VocabularyAudio nếu thành công, None nếu failed
        """
        try:
            # Kiểm tra nếu đã có audio
            if vocabulary.audios:
                logger.debug(f"Vocabulary {vocabulary.id} đã có audio, skip")
                return vocabulary.audios[0]
            
            # Tạo thư mục nếu chưa có
            user_audio_dir = AUDIO_DIR / str(vocabulary.user_id)
            user_audio_dir.mkdir(parents=True, exist_ok=True)
            
            # Đường dẫn file
            filename = f"{vocabulary.id}.mp3"
            audio_path = str(user_audio_dir / filename)
            audio_url = f"/static/audio/{vocabulary.user_id}/{filename}"
            
            # Generate audio với Edge-TTS
            import edge_tts
            
            communicate = edge_tts.Communicate(vocabulary.word, voice)
            await communicate.save(audio_path)
            
            # Lưu vào database
            vocab_audio = VocabularyAudio(
                vocabulary_id=vocabulary.id,
                audio_path=audio_path,
                audio_url=audio_url,
                tts_provider="edge-tts",
                voice=voice,
                language=language
            )
            
            self.db.add(vocab_audio)
            self.db.commit()
            self.db.refresh(vocab_audio)
            
            logger.info(f"Generated audio for vocabulary '{vocabulary.word}' (ID: {vocabulary.id})")
            return vocab_audio
            
        except Exception as e:
            logger.error(f"Failed to generate audio for vocabulary {vocabulary.id}: {e}")
            self.db.rollback()
            return None
    
    async def generate_audio_for_vocab_id(
        self,
        vocab_id: int,
        voice: str = DEFAULT_VOICE,
        language: str = DEFAULT_LANGUAGE
    ) -> Optional[VocabularyAudio]:
        """
        Generate audio cho vocabulary by ID.
        """
        vocabulary = self.db.get(Vocabulary, vocab_id)
        if not vocabulary:
            logger.warning(f"Vocabulary {vocab_id} not found")
            return None
        
        return await self.generate_audio(vocabulary, voice, language)
    
    def get_audio_url(self, vocabulary_id: int) -> Optional[str]:
        """
        Lấy audio URL cho vocabulary.
        """
        vocab = self.db.get(Vocabulary, vocabulary_id)
        if vocab and vocab.audios:
            return vocab.audios[0].audio_url
        return None
