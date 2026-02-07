"""
Vocabulary Service Layer - Business logic cho vocabulary management và SRS.
Updated để hỗ trợ multiple meanings và import/export.
"""
import csv
import io
import json
from datetime import datetime
from typing import Optional, List, Generator, Literal
from dataclasses import dataclass, field

from sqlmodel import Session, select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models.vocabulary import Vocabulary
from app.models.vocabulary_meaning import VocabularyMeaning
from app.models.review_history import ReviewHistory
from app.models.generated_question import GeneratedQuestion
from app.models.enums import (
    ReviewQuality, PracticeType, WordType, MeaningSource,
    QuestionType, QuestionDifficulty
)
from app.schemas.vocabulary import (
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyReview,
    VocabularyStatsResponse,
    MeaningCreate
)
from app.schemas.quiz import QuizQuestion, QuizSessionResponse
from app.core.logging import get_logger
from app.core.srs_engine import SRSEngine, SRSState, ReviewQuality as SRSReviewQuality
from app.ai.factory import get_ai_provider
from app.services.dictionary_service import DictionaryService

logger = get_logger(__name__)


# Danh sách Function Words tiêu chuẩn
FUNCTION_WORDS = {
    # Articles
    "a", "an", "the",
    # Prepositions
    "in", "on", "at", "to", "for", "with", "by", "from", "of", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "over", "out", "up", "down", "off", "against",
    # Conjunctions
    "and", "or", "but", "so", "yet", "nor", "for", "because", "although",
    "while", "if", "unless", "until", "when", "where", "whether",
    # Pronouns
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
    "my", "your", "his", "her", "its", "our", "their",
    "mine", "yours", "hers", "ours", "theirs",
    "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves",
    "this", "that", "these", "those", "who", "whom", "whose", "which", "what",
    # Auxiliary verbs
    "is", "am", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having",
    "do", "does", "did", "doing",
    "will", "would", "shall", "should",
    "can", "could", "may", "might", "must",
    # Determiners
    "some", "any", "no", "every", "each", "all", "both", "few", "many",
    "much", "more", "most", "other", "another", "such",
    # Particles
    "not", "very", "too", "also", "just", "only", "even", "still", "already",
}


@dataclass
class ImportResult:
    """Kết quả của quá trình import từ vựng."""
    total_processed: int = 0
    new_words: int = 0
    merged_meanings: int = 0
    auto_generated_count: int = 0
    failed_auto_meaning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    created_vocab_ids: List[int] = field(default_factory=list)  # Track vocab IDs for background tasks


class VocabularyService:
    """
    Service layer cho vocabulary management.
    Implement business logic cho CRUD operations, SRS algorithm, import/export.
    """
    
    # Question Pool Management Constants
    MAX_POOL_SIZE = 5        # Tối đa 5 câu hỏi cho mỗi từ vựng
    USAGE_THRESHOLD = 3      # Mỗi câu dùng tối đa 3 lần trước khi refresh
    
    def __init__(self, session: Session):
        """
        Initialize vocabulary service.
        
        Args:
            session: Database session
        """
        self.session = session
        self._dictionary_service: Optional[DictionaryService] = None
    
    @property
    def dictionary_service(self) -> DictionaryService:
        """Lazy-load dictionary service."""
        if self._dictionary_service is None:
            self._dictionary_service = DictionaryService(self.session)
        return self._dictionary_service
    
    @staticmethod
    def normalize_word(word: str) -> str:
        """Normalize word: trim, lowercase, remove duplicate spaces."""
        return " ".join(word.strip().lower().split())
    
    @staticmethod
    def classify_word(word: str, manual_override: Optional[WordType] = None) -> tuple[WordType, bool]:
        """
        Phân loại từ thành Function Word hoặc Content Word.
        
        Args:
            word: Từ cần phân loại
            manual_override: Override manual nếu có
            
        Returns:
            Tuple (word_type, is_manual)
        """
        if manual_override is not None:
            return manual_override, True
        
        normalized = VocabularyService.normalize_word(word)
        word_type = WordType.FUNCTION_WORD if normalized in FUNCTION_WORDS else WordType.CONTENT_WORD
        return word_type, False
    
    def create_vocab(
        self,
        user_id: int,
        vocab_data: VocabularyCreate
    ) -> Vocabulary:
        """
        Tạo vocabulary mới cho user với multiple meanings.
        
        Args:
            user_id: ID của user
            vocab_data: Data để tạo vocabulary
            
        Returns:
            Vocabulary đã được tạo
            
        Raises:
            ValueError: Nếu vocabulary đã tồn tại cho user
        """
        try:
            # Normalize word
            normalized_word = self.normalize_word(vocab_data.word)
            
            # Classify word
            word_type, is_manual = self.classify_word(
                normalized_word, 
                getattr(vocab_data, 'word_type', None)
            )
            
            # Tạo vocabulary với SRS defaults
            vocab = Vocabulary(
                user_id=user_id,
                word=normalized_word,
                word_type=word_type,
                is_word_type_manual=is_manual,
                # SRS defaults
                easiness_factor=2.5,
                interval=0,
                repetitions=0,
                next_review_date=datetime.utcnow()
            )
            
            self.session.add(vocab)
            self.session.flush()  # Flush để lấy vocab.id
            
            # Thêm meanings
            for meaning_data in vocab_data.meanings:
                meaning = VocabularyMeaning(
                    vocabulary_id=vocab.id,
                    definition=meaning_data.definition,
                    meaning_source=MeaningSource.MANUAL,
                    is_auto_generated=False
                )
                self.session.add(meaning)
                
                # Lưu example_sentence nếu có và chuyển nó vào VocabularyContext
                # Thay vì làm ô nhiễm VocabularyMeaning
                if hasattr(meaning_data, 'example_sentence') and meaning_data.example_sentence:
                    from app.models.vocabulary_context import VocabularyContext
                    context = VocabularyContext(
                        vocabulary_id=vocab.id,
                        sentence=meaning_data.example_sentence,
                        ai_provider="import" if is_manual else "manual"
                    )
                    self.session.add(context)
            
            self.session.commit()
            self.session.refresh(vocab)
            
            logger.info(f"Created vocabulary '{vocab.word}' with {len(vocab_data.meanings)} meanings for user {user_id}")
            return vocab
            
        except IntegrityError as e:
            self.session.rollback()
            logger.warning(f"Vocabulary '{vocab_data.word}' already exists for user {user_id}")
            raise ValueError(f"Vocabulary '{vocab_data.word}' đã tồn tại") from e
    
    def add_meaning(
        self,
        vocab_id: int,
        user_id: int,
        meaning_data: MeaningCreate,
        source: MeaningSource = MeaningSource.MANUAL,
        is_auto: bool = False
    ) -> Optional[VocabularyMeaning]:
        """
        Thêm meaning mới cho vocabulary.
        
        Args:
            vocab_id: ID của vocabulary
            user_id: ID của user
            meaning_data: Data của meaning
            source: Nguồn của meaning
            is_auto: True nếu auto-generated
            
        Returns:
            VocabularyMeaning đã tạo, hoặc None nếu vocabulary không tồn tại
        """
        vocab = self.session.get(Vocabulary, vocab_id)
        if not vocab or vocab.user_id != user_id:
            return None
        
        # Check duplicate meaning
        existing_meanings = [m.definition.lower().strip() for m in vocab.meanings]
        if meaning_data.definition.lower().strip() in existing_meanings:
            logger.debug(f"Duplicate meaning skipped for vocab {vocab_id}")
            return None
        
        meaning = VocabularyMeaning(
            vocabulary_id=vocab_id,
            definition=meaning_data.definition,
            meaning_source=source,
            is_auto_generated=is_auto
        )
        
        self.session.add(meaning)
        self.session.commit()
        self.session.refresh(meaning)
        
        return meaning
    
    def update_vocab(
        self,
        vocab_id: int,
        user_id: int,
        vocab_data: VocabularyUpdate
    ) -> Optional[Vocabulary]:
        """
        Update vocabulary của user.
        
        Args:
            vocab_id: ID của vocabulary
            user_id: ID của user
            vocab_data: Data để update
            
        Returns:
            Vocabulary đã được update, hoặc None nếu không tìm thấy
        """
        vocab = self.session.get(Vocabulary, vocab_id)
        if not vocab or vocab.user_id != user_id:
            logger.warning(f"Vocabulary {vocab_id} not found for user {user_id}")
            return None
        
        # Update các fields được cung cấp
        update_data = vocab_data.model_dump(exclude_unset=True)
        
        # Handle word normalization
        if 'word' in update_data:
            update_data['word'] = self.normalize_word(update_data['word'])
        
        # Handle word_type override
        if 'word_type' in update_data and update_data['word_type'] is not None:
            update_data['is_word_type_manual'] = True
        
        for attr, value in update_data.items():
            if attr != 'meanings':  # Meanings handled separately
                setattr(vocab, attr, value)
        
        try:
            self.session.add(vocab)
            self.session.commit()
            self.session.refresh(vocab)
            
            logger.info(f"Updated vocabulary {vocab_id} for user {user_id}")
            return vocab
            
        except IntegrityError as e:
            self.session.rollback()
            logger.warning(f"Update failed - word conflict for user {user_id}")
            raise ValueError(f"Vocabulary đã tồn tại") from e
    
    def delete_vocab(self, vocab_id: int, user_id: int) -> bool:
        """Xóa vocabulary của user."""
        vocab = self.session.get(Vocabulary, vocab_id)
        if not vocab or vocab.user_id != user_id:
            return False
        
        self.session.delete(vocab)
        self.session.commit()
        
        logger.info(f"Deleted vocabulary {vocab_id} for user {user_id}")
        return True

    def get_vocab(self, vocab_id: int, user_id: int) -> Optional[Vocabulary]:
        """Lấy thông tin chi tiết một vocabulary với meanings và contexts."""
        query = select(Vocabulary).where(
            Vocabulary.id == vocab_id,
            Vocabulary.user_id == user_id
        ).options(
            selectinload(Vocabulary.meanings),
            selectinload(Vocabulary.contexts)
        )
        
        return self.session.exec(query).first()
    
    def get_vocab_list(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        word_type: Optional[WordType] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Vocabulary], int]:
        """
        Lấy danh sách vocabularies của user với filters.
        """
        # Base query với eager loading meanings và contexts
        query = select(Vocabulary).where(
            Vocabulary.user_id == user_id
        ).options(
            selectinload(Vocabulary.meanings),
            selectinload(Vocabulary.contexts)
        )
        
        # Apply filters
        if word_type:
            query = query.where(Vocabulary.word_type == word_type)
        
        if status:
            if status.upper() == "DUE":
                query = query.where(Vocabulary.next_review_date <= datetime.utcnow())
            elif status.upper() == "LEARNED":
                query = query.where(Vocabulary.repetitions > 0)
            elif status.upper() == "LEARNING":
                query = query.where(Vocabulary.repetitions == 0)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(Vocabulary.word.ilike(search_pattern))
        
        # Count total
        count_query = select(func.count()).select_from(
            select(Vocabulary).where(Vocabulary.user_id == user_id).subquery()
        )
        if word_type:
            count_query = select(func.count()).select_from(query.subquery())
        total = self.session.exec(count_query).one()
        
        # Apply pagination và order
        query = query.order_by(Vocabulary.next_review_date.asc()).offset(skip).limit(limit)
        
        vocabularies = list(self.session.exec(query).all())
        
        logger.info(f"Retrieved {len(vocabularies)} vocabularies for user {user_id}")
        return vocabularies, total
    
    def get_vocab_by_word(self, user_id: int, word: str) -> Optional[Vocabulary]:
        """Tìm vocabulary theo word (normalized) với meanings và contexts."""
        normalized = self.normalize_word(word)
        query = select(Vocabulary).where(
            Vocabulary.user_id == user_id,
            Vocabulary.word == normalized
        ).options(
            selectinload(Vocabulary.meanings),
            selectinload(Vocabulary.contexts)
        )
        
        return self.session.exec(query).first()
    
    async def import_from_txt(
        self,
        user_id: int,
        content: str,
        batch_size: int = 100,
        auto_fetch_meaning: bool = True
    ) -> ImportResult:
        """
        Import từ vựng từ TXT content.
        
        Format mỗi dòng: word|definition|example (definition và example optional)
        
        Args:
            user_id: ID của user
            content: Nội dung file TXT
            batch_size: Không sử dụng (giữ để tương thích)
            auto_fetch_meaning: Tự động dịch từ nếu không có definition
            
        Returns:
            ImportResult với thống kê chi tiết
        """
        result = ImportResult()
        lines = content.strip().split('\n')
        
        logger.info(f"Starting import: {len(lines)} lines, auto_fetch={auto_fetch_meaning}")
        
        # Process từng dòng
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            result.total_processed += 1
            
            try:
                # Parse: word|definition|example
                parts = line.split('|')
                word = self.normalize_word(parts[0]) if parts else ""
                
                if not word:
                    result.warnings.append(f"Line {line_num}: Empty word")
                    continue
                
                definition = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
                
                # Xác định definition
                final_definition = None
                meaning_source = MeaningSource.MANUAL
                is_auto = False
                
                # Dịch definition nếu có
                if definition:
                    translated = await self.dictionary_service.translate_text(definition)
                    final_definition = translated if translated else definition
                    if translated:
                        meaning_source = MeaningSource.AUTO_TRANSLATE
                        is_auto = True
                
                # Dịch từ nếu không có definition và auto_fetch = True
                elif auto_fetch_meaning:
                    translated = await self.dictionary_service.translate_text(word)
                    if translated:
                        final_definition = translated
                        meaning_source = MeaningSource.AUTO_TRANSLATE
                        is_auto = True
                        result.auto_generated_count += 1
                
                # Nếu không có definition
                if not final_definition:
                    result.failed_auto_meaning.append(word)
                    result.warnings.append(f"Line {line_num}: No definition for '{word}'")
                    self._create_or_merge_vocab(user_id, word, None, result)
                    continue
                
                # Tạo hoặc merge vocabulary
                self._create_or_merge_vocab(
                    user_id, word, final_definition,
                    result, meaning_source, is_auto
                )
                
            except Exception as e:
                result.errors.append(f"Line {line_num}: {str(e)}")
                logger.error(f"Import error at line {line_num}: {e}")
        
        # Commit
        self.session.commit()
        
        logger.info(
            f"Import done: {result.new_words} new, {result.merged_meanings} merged, "
            f"{result.auto_generated_count} auto, {len(result.failed_auto_meaning)} failed"
        )
        
        return result
    
    async def import_from_txt_stream(
        self,
        user_id: int,
        content: str,
        auto_fetch_meaning: bool = True,
        batch_commit_size: int = 50
    ):
        """
        Import từ vựng với streaming progress updates (SSE).
        
        Yield events:
        - progress: {"type": "progress", "data": {"current": N, "total": M, "percent": X}}
        - item_processed: {"type": "item_processed", "data": {"word": "...", "status": "success|failed", "message": "..."}}
        - completed: {"type": "completed", "data": ImportResult}
        - error: {"type": "error", "data": {"message": "..."}}
        
        Args:
            user_id: ID của user
            content: Nội dung file TXT
            auto_fetch_meaning: Tự động dịch từ nếu không có definition
            batch_commit_size: Commit database sau mỗi N items
        
        Yields:
            Dict với event type và data
        """
        result = ImportResult()
        lines = content.strip().split('\n')
        
        # Đếm số dòng hợp lệ
        valid_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        total = len(valid_lines)
        
        logger.info(f"Starting streaming import: {total} valid lines, auto_fetch={auto_fetch_meaning}")
        
        # Yield initial progress
        yield {
            "type": "progress",
            "data": {"current": 0, "total": total, "percent": 0}
        }
        
        processed_count = 0
        batch_buffer = []
        
        # Process từng dòng
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            processed_count += 1
            result.total_processed += 1
            
            try:
                # Parse: word|definition|example
                parts = line.split('|')
                word = self.normalize_word(parts[0]) if parts else ""
                
                if not word:
                    result.warnings.append(f"Line {line_num}: Empty word")
                    yield {
                        "type": "item_processed",
                        "data": {
                            "word": f"Line {line_num}",
                            "status": "warning",
                            "message": "Empty word"
                        }
                    }
                    continue
                
                definition = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
                
                # Xác định definition
                final_definition = None
                meaning_source = MeaningSource.MANUAL
                is_auto = False
                
                # Dịch definition nếu có
                if definition:
                    translated = await self.dictionary_service.translate_text(definition)
                    final_definition = translated if translated else definition
                    if translated:
                        meaning_source = MeaningSource.AUTO_TRANSLATE
                        is_auto = True
                
                # Dịch từ nếu không có definition và auto_fetch = True
                elif auto_fetch_meaning:
                    translated = await self.dictionary_service.translate_text(word)
                    if translated:
                        final_definition = translated
                        meaning_source = MeaningSource.AUTO_TRANSLATE
                        is_auto = True
                        result.auto_generated_count += 1
                
                # Nếu không có definition
                if not final_definition:
                    result.failed_auto_meaning.append(word)
                    result.warnings.append(f"Line {line_num}: No definition for '{word}'")
                    self._create_or_merge_vocab(user_id, word, None, result)
                    
                    yield {
                        "type": "item_processed",
                        "data": {
                            "word": word,
                            "status": "warning",
                            "message": "No definition found"
                        }
                    }
                else:
                    # Tạo hoặc merge vocabulary
                    self._create_or_merge_vocab(
                        user_id, word, final_definition,
                        result, meaning_source, is_auto
                    )
                    
                    yield {
                        "type": "item_processed",
                        "data": {
                            "word": word,
                            "status": "success",
                            "message": f"Added: {final_definition[:50]}...",
                            "vocab_id": result.created_vocab_ids[-1] if result.created_vocab_ids else None
                        }
                    }
                
                # Batch commit
                batch_buffer.append(word)
                if len(batch_buffer) >= batch_commit_size:
                    self.session.commit()
                    logger.debug(f"Batch committed: {len(batch_buffer)} items")
                    batch_buffer.clear()
                
            except Exception as e:
                error_msg = str(e)
                result.errors.append(f"Line {line_num}: {error_msg}")
                logger.error(f"Import error at line {line_num}: {e}")
                
                yield {
                    "type": "item_processed",
                    "data": {
                        "word": word if 'word' in locals() else f"Line {line_num}",
                        "status": "failed",
                        "message": error_msg
                    }
                }
            
            # Yield progress update
            percent = int((processed_count / total) * 100) if total > 0 else 100
            yield {
                "type": "progress",
                "data": {
                    "current": processed_count,
                    "total": total,
                    "percent": percent
                }
            }
        
        # Final commit
        if batch_buffer:
            self.session.commit()
            logger.debug(f"Final commit: {len(batch_buffer)} items")
        
        logger.info(
            f"Streaming import done: {result.new_words} new, {result.merged_meanings} merged, "
            f"{result.auto_generated_count} auto, {len(result.failed_auto_meaning)} failed"
        )
        
        # Yield completion event
        yield {
            "type": "completed",
            "data": {
                "total_processed": result.total_processed,
                "new_words": result.new_words,
                "merged_meanings": result.merged_meanings,
                "auto_generated_count": result.auto_generated_count,
                "failed_auto_meaning": result.failed_auto_meaning,
                "warnings": result.warnings,
                "errors": result.errors
            }
        }
    

    def _create_or_merge_vocab(
        self,
        user_id: int,
        word: str,
        definition: Optional[str],
        result: ImportResult,
        source: MeaningSource = MeaningSource.MANUAL,
        is_auto: bool = False
    ):
        """Helper để tạo hoặc merge vocabulary."""
        existing = self.get_vocab_by_word(user_id, word)
        
        if existing:
            # Merge: thêm meaning mới nếu chưa có
            if definition:
                existing_defs = [m.definition.lower().strip() for m in existing.meanings]
                if definition.lower().strip() not in existing_defs:
                    meaning = VocabularyMeaning(
                        vocabulary_id=existing.id,
                        definition=definition,
                        meaning_source=source,
                        is_auto_generated=is_auto
                    )
                    self.session.add(meaning)
                    result.merged_meanings += 1
            
            # Track ID for background tasks
            if existing.id not in result.created_vocab_ids:
                result.created_vocab_ids.append(existing.id)
                
        else:
            # Create new vocabulary
            word_type, is_manual = self.classify_word(word)
            
            vocab = Vocabulary(
                user_id=user_id,
                word=word,
                word_type=word_type,
                is_word_type_manual=is_manual,
                easiness_factor=2.5,
                interval=0,
                repetitions=0,
                next_review_date=datetime.utcnow()
            )
            self.session.add(vocab)
            self.session.flush()  # Get ID
            
            if definition:
                meaning = VocabularyMeaning(
                    vocabulary_id=vocab.id,
                    definition=definition,
                    meaning_source=source,
                    is_auto_generated=is_auto
                )
                self.session.add(meaning)
            
            result.new_words += 1
            result.created_vocab_ids.append(vocab.id)
    
    def export_vocabularies(
        self,
        user_id: int,
        format: Literal["json", "txt", "csv"] = "json",
        page: Optional[int] = None,
        page_size: int = 1000
    ) -> str:
        """
        Export vocabularies của user sang các format khác nhau.
        
        Args:
            user_id: ID của user
            format: Format export (json, txt, csv)
            page: Page number (optional, None = all)
            page_size: Số records mỗi page
            
        Returns:
            String content theo format được chọn
        """
        # Query vocabularies với meanings
        query = select(Vocabulary).where(
            Vocabulary.user_id == user_id
        ).options(selectinload(Vocabulary.meanings))
        
        if page is not None:
            skip = (page - 1) * page_size
            query = query.offset(skip).limit(page_size)
        
        vocabularies = list(self.session.exec(query).all())
        
        if format == "json":
            return self._export_to_json(vocabularies)
        elif format == "txt":
            return self._export_to_txt(vocabularies)
        elif format == "csv":
            return self._export_to_csv(vocabularies)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_to_json(self, vocabularies: List[Vocabulary]) -> str:
        """Export sang JSON format."""
        data = []
        for vocab in vocabularies:
            vocab_data = {
                "word": vocab.word,
                "word_type": vocab.word_type.value,
                "meanings": [
                    {
                        "definition": m.definition,
                        "source": m.meaning_source.value
                    }
                    for m in vocab.meanings
                ],
                "srs": {
                    "easiness_factor": vocab.easiness_factor,
                    "interval": vocab.interval,
                    "repetitions": vocab.repetitions,
                    "next_review_date": vocab.next_review_date.isoformat()
                }
            }
            data.append(vocab_data)
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _export_to_txt(self, vocabularies: List[Vocabulary]) -> str:
        """
        Export sang TXT format.
        Format: word|definition|example (một dòng cho mỗi meaning)
        """
        lines = []
        for vocab in vocabularies:
            for meaning in vocab.meanings:
                parts = [vocab.word, meaning.definition]
                lines.append("|".join(parts))
        
        return "\n".join(lines)
    
    def _export_to_csv(self, vocabularies: List[Vocabulary]) -> str:
        """Export sang CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "word", "word_type", "definition", "example_sentence",
            "meaning_source", "easiness_factor", "interval", "repetitions"
        ])
        
        # Data
        for vocab in vocabularies:
            for meaning in vocab.meanings:
                writer.writerow([
                    vocab.word,
                    vocab.word_type.value,
                    meaning.definition,
                    "", # example_sentence legacy placeholder
                    meaning.meaning_source.value,
                    vocab.easiness_factor,
                    vocab.interval,
                    vocab.repetitions
                ])
        
        return output.getvalue()
    
    def update_learning_status(
        self,
        vocab_id: int,
        user_id: int,
        review_data: VocabularyReview,
        update_srs: bool = True
    ) -> Optional[Vocabulary]:
        """
        Update learning status của vocabulary sau khi review (SRS algorithm).
        
        Args:
            vocab_id: ID của vocabulary
            user_id: ID của user
            review_data: Data review (quality, time_spent)
            update_srs: Có update SRS algorithm không (True: Review, False: Quiz/Practice)
        """
        vocab = self.session.get(Vocabulary, vocab_id)
        if not vocab or vocab.user_id != user_id:
            return None
        
        # Lưu review history
        review_history = ReviewHistory(
            user_id=user_id,
            vocabulary_id=vocab_id,
            review_quality=review_data.review_quality,
            time_spent_seconds=review_data.time_spent_seconds,
            reviewed_at=datetime.utcnow()
        )
        self.session.add(review_history)
        
        # Chỉ update SRS nếu được yêu cầu (Review mode)
        if update_srs:
            # Chuyển đổi trạng thái hiện tại sang SRSState
            current_srs_state = SRSState(
                easiness_factor=vocab.easiness_factor,
                interval=vocab.interval,
                repetitions=vocab.repetitions,
                next_review_date=vocab.next_review_date
            )
            
            # Gọi SRSEngine để tính toán trạng thái mới
            quality = SRSReviewQuality(review_data.review_quality.value)
            new_srs_state = SRSEngine.update_after_review(
                current_state=current_srs_state,
                review_quality=quality,
                time_spent_seconds=review_data.time_spent_seconds
            )
            
            # Cập nhật lại model
            vocab.easiness_factor = new_srs_state.easiness_factor
            vocab.interval = new_srs_state.interval
            vocab.repetitions = new_srs_state.repetitions
            vocab.next_review_date = new_srs_state.next_review_date
            
            self.session.add(vocab)
            logger.info(f"Updated SRS for vocab {vocab_id}: EF={vocab.easiness_factor:.2f}")
        else:
            logger.info(f"Recorded practice for vocab {vocab_id} (No SRS update)")
        
        self.session.commit()
        self.session.refresh(vocab)
        
        return vocab
    
    def get_vocab_stats(self, user_id: int) -> VocabularyStatsResponse:
        """Lấy thống kê vocabularies của user."""
        # Total
        total = self.session.exec(
            select(func.count()).select_from(Vocabulary).where(
                Vocabulary.user_id == user_id
            )
        ).one()
        
        # Due today
        due_today = self.session.exec(
            select(func.count()).select_from(Vocabulary).where(
                and_(
                    Vocabulary.user_id == user_id,
                    Vocabulary.next_review_date <= datetime.utcnow()
                )
            )
        ).one()
        
        # Learned
        learned = self.session.exec(
            select(func.count()).select_from(Vocabulary).where(
                and_(
                    Vocabulary.user_id == user_id,
                    Vocabulary.repetitions > 0
                )
            )
        ).one()
        
        # By word type
        by_word_type = {}
        for wt in WordType:
            count = self.session.exec(
                select(func.count()).select_from(Vocabulary).where(
                    and_(
                        Vocabulary.user_id == user_id,
                        Vocabulary.word_type == wt
                    )
                )
            ).one()
            by_word_type[wt.value] = count
        
        return VocabularyStatsResponse(
            total_vocabularies=total,
            due_today=due_today,
            learned=learned,
            learning=total - learned,
            by_word_type=by_word_type
        )

    async def generate_quiz_session(
        self,
        user_id: int,
        limit: int = 10
    ) -> QuizSessionResponse:
        """Tạo phiên quiz trắc nghiệm sử dụng AI."""
        # 1. Lấy due vocabularies (ưu tiên)
        query = select(Vocabulary).where(
            and_(
                Vocabulary.user_id == user_id,
                Vocabulary.next_review_date <= datetime.utcnow()
            )
        ).options(selectinload(Vocabulary.meanings)).order_by(
            Vocabulary.next_review_date.asc()
        ).limit(limit)
        
        due_vocabs = list(self.session.exec(query).all())
        quiz_vocabs = list(due_vocabs)
        
        # 2. Nếu thiếu, lấy thêm random learned words (Unlimited Practice)
        remaining = limit - len(quiz_vocabs)
        if remaining > 0:
            # Lấy list ID đã chọn để loại trừ
            selected_ids = [v.id for v in quiz_vocabs]
            
            # Query random learned words (repetitions > 0)
            filler_query = select(Vocabulary).where(
                Vocabulary.user_id == user_id,
                Vocabulary.repetitions > 0  # Chỉ lấy từ đã học
            )
            
            if selected_ids:
                filler_query = filler_query.where(Vocabulary.id.notin_(selected_ids))
            
            filler_query = filler_query.options(selectinload(Vocabulary.meanings)).order_by(
                func.random()
            ).limit(remaining)
            
            filler_vocabs = list(self.session.exec(filler_query).all())
            quiz_vocabs.extend(filler_vocabs)
            
            if filler_vocabs:
                logger.info(f"Added {len(filler_vocabs)} filler words for quiz session")
        
        # 3. Nếu vẫn chưa đủ (ví dụ user mới học ít từ), lấy thêm từ mới (optional)
        # Hiện tại chỉ cần learned words là đủ cho practice
        
        if not quiz_vocabs:
            return QuizSessionResponse(questions=[])
        
        # 4. Generate questions (Smart Reuse Strategy)
        ai_provider = get_ai_provider()
        questions = []
        import random 
        
        for vocab in quiz_vocabs:
            try:
                # 4a. Check cache (GeneratedQuestion)
                # Lấy tất cả câu hỏi đã từng generate cho từ này (loại Multiple Choice)
                cached_questions = self.session.exec(
                    select(GeneratedQuestion).where(
                        GeneratedQuestion.vocabulary_id == vocab.id,
                        GeneratedQuestion.question_type == QuestionType.MULTIPLE_CHOICE
                    )
                ).all()
                
                quiz_question = None
                should_generate_new = False
                
                if cached_questions:
                    # Filter candidates for reuse (usage_count < THRESHOLD)
                    candidates = [q for q in cached_questions if q.usage_count < self.USAGE_THRESHOLD]
                    
                    if candidates:
                        # Case 1: Reuse existing question (Weighted Random)
                        # Shuffle để tăng tính ngẫu nhiên khi có nhiều câu cùng usage_count
                        random.shuffle(candidates)
                        weights = [1.0 / (q.usage_count + 1) for q in candidates]
                        selected_q = random.choices(candidates, weights=weights, k=1)[0]
                        
                        # Update usage count
                        selected_q.usage_count += 1
                        self.session.add(selected_q)
                        self.session.commit()
                        
                        # Parse data
                        q_data = selected_q.question_data
                        quiz_question = self._parse_quiz_question(vocab, q_data)
                        logger.info(f"✓ Reused question for '{vocab.word}' (Usage: {selected_q.usage_count}/{len(cached_questions)} total)")
                        
                    else:
                        # Case 2: All questions used up (usage_count >= THRESHOLD)
                        # Chiến lược: Generate mới + Recycle một số câu cũ để tạo sự đa dạng cho lần sau
                        
                        # 1. Xử lý Pool Size
                        if len(cached_questions) >= self.MAX_POOL_SIZE:
                            # Pool full → Delete oldest
                            oldest_q = min(cached_questions, key=lambda q: q.created_at)
                            self.session.delete(oldest_q)
                            
                            # Danh sách còn lại để recycle
                            remaining_questions = [q for q in cached_questions if q.id != oldest_q.id]
                            logger.info(f"♻️  Pool full for '{vocab.word}', deleting oldest (ID: {oldest_q.id})")
                        else:
                            remaining_questions = cached_questions
                            logger.info(f"➕ Pool not full for '{vocab.word}', adding new question")

                        # 2. Recycle (Reset usage) một số câu hỏi cũ để mix với câu mới
                        # Mục đích: Tránh việc câu mới vừa tạo trở thành candidate duy nhất
                        if remaining_questions:
                            # Recycle 50% số lượng còn lại hoặc tối thiểu 2 câu
                            recycle_count = min(len(remaining_questions), 2)
                            recycled_qs = random.sample(remaining_questions, recycle_count)
                            
                            for q in recycled_qs:
                                q.usage_count = 0
                                self.session.add(q)
                            
                            logger.info(f"🔄 Recycled {len(recycled_qs)} old questions to mix with new one")

                        self.session.commit()
                        should_generate_new = True
                else:
                    # Case 3: No cached questions yet
                    should_generate_new = True
                    logger.info(f"🆕 No cached questions for '{vocab.word}', generating first question")
                
                
                if should_generate_new:
                    # Generate New Question via AI
                    logger.info(f"Generating new question for vocab {vocab.id} ({vocab.word})")
                    
                    # Lấy definition đầu tiên cho quiz
                    definition = vocab.meanings[0].definition if vocab.meanings else ""
                    
                    try:
                        ai_q = await ai_provider.generate_question(
                            vocab=vocab,
                            practice_type=PracticeType.MULTIPLE_CHOICE
                        )
                        
                        # Save to Cache (GeneratedQuestion)
                        new_generated_q = GeneratedQuestion(
                            user_id=user_id,
                            vocabulary_id=vocab.id,
                            question_type=QuestionType.MULTIPLE_CHOICE,
                            difficulty=QuestionDifficulty.MEDIUM,
                            question_data=ai_q.dict(), # Save AI response as JSON
                            is_used=False,
                            usage_count=1 # Initialize usage count
                        )
                        self.session.add(new_generated_q)
                        self.session.commit() 
                        
                        quiz_question = QuizQuestion(
                            id=vocab.id,
                            word=vocab.word,
                            question_text=ai_q.question_text,
                            options=ai_q.options or {},
                            correct_answer=ai_q.correct_answer,
                            explanation=ai_q.explanation or "",
                            grammar_explanation=ai_q.grammar_explanation
                        )
                        logger.info(f"Successfully generated new question for {vocab.word}")
                    except Exception as gen_error:
                        logger.error(f"Failed to generate question for vocab {vocab.id} ({vocab.word}): {gen_error}", exc_info=True)
                        raise  # Re-raise để outer exception handler xử lý

                questions.append(quiz_question)
                
            except Exception as e:
                logger.error(f"Error generating quiz for vocab {vocab.id} ({vocab.word}): {e}", exc_info=True)
                continue
        
        return QuizSessionResponse(questions=questions)

    def _parse_quiz_question(self, vocab: Vocabulary, q_data: dict) -> QuizQuestion:
        """Helper to parse raw JSON data into QuizQuestion model."""
        # Handle options - có thể là dict hoặc list (dữ liệu cũ)
        options_raw = q_data.get("options", {})
        correct_answer_raw = q_data.get("correct_answer", "")
        
        if isinstance(options_raw, list):
            # Convert list to dict với keys A, B, C, D
            options = {chr(65 + i): opt for i, opt in enumerate(options_raw)}
            
            # Convert correct_answer nếu nó là text (tìm trong list)
            if correct_answer_raw and correct_answer_raw not in ["A", "B", "C", "D"]:
                # correct_answer là text → Tìm index trong list
                try:
                    idx = options_raw.index(correct_answer_raw)
                    correct_answer = chr(65 + idx)  # Convert index to A, B, C, D
                except ValueError:
                    # Không tìm thấy → Giữ nguyên
                    correct_answer = correct_answer_raw
            else:
                # correct_answer đã là A/B/C/D → Giữ nguyên
                correct_answer = correct_answer_raw
                
        elif isinstance(options_raw, dict):
            options = options_raw
            correct_answer = correct_answer_raw
        else:
            options = {}
            correct_answer = correct_answer_raw
        
        return QuizQuestion(
            id=vocab.id,
            word=vocab.word,
            question_text=q_data.get("question_text", ""),
            options=options,
            correct_answer=correct_answer,
            explanation=q_data.get("explanation", ""),
            grammar_explanation=q_data.get("grammar_explanation", "")
        )
