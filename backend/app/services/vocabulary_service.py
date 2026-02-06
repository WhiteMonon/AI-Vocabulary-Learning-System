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
from app.models.enums import (
    ReviewQuality, PracticeType, WordType, MeaningSource
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


class VocabularyService:
    """
    Service layer cho vocabulary management.
    Implement business logic cho CRUD operations, SRS algorithm, import/export.
    """
    
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
                    example_sentence=meaning_data.example_sentence,
                    meaning_source=MeaningSource.MANUAL,
                    is_auto_generated=False
                )
                self.session.add(meaning)
            
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
            example_sentence=meaning_data.example_sentence,
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
        """Lấy thông tin chi tiết một vocabulary với meanings."""
        query = select(Vocabulary).where(
            Vocabulary.id == vocab_id,
            Vocabulary.user_id == user_id
        ).options(selectinload(Vocabulary.meanings))
        
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
        # Base query với eager loading meanings
        query = select(Vocabulary).where(
            Vocabulary.user_id == user_id
        ).options(selectinload(Vocabulary.meanings))
        
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
        """Tìm vocabulary theo word (normalized)."""
        normalized = self.normalize_word(word)
        query = select(Vocabulary).where(
            Vocabulary.user_id == user_id,
            Vocabulary.word == normalized
        ).options(selectinload(Vocabulary.meanings))
        
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
            batch_size: Số lượng records xử lý mỗi batch
            auto_fetch_meaning: Tự động fetch meaning nếu không có
            
        Returns:
            ImportResult với thống kê chi tiết
        """
        result = ImportResult()
        lines = content.strip().split('\n')
        
        # Collect words cần auto-fetch meaning
        words_need_meaning: List[str] = []
        parsed_entries: List[tuple] = []  # (word, definition, example)
        
        # Parse all lines first
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines và comments
                continue
            
            result.total_processed += 1
            
            # Parse line: word|definition|example
            parts = line.split('|')
            word = self.normalize_word(parts[0]) if parts else ""
            
            if not word:
                result.warnings.append(f"Line {line_num}: Empty word skipped")
                continue
            
            definition = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
            example = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
            
            parsed_entries.append((word, definition, example, line_num))
            
            if not definition and auto_fetch_meaning:
                words_need_meaning.append(word)
        
        # Batch fetch meanings cho words không có definition
        auto_meanings: dict = {}
        if words_need_meaning:
            logger.info(f"Auto-fetching meanings for {len(words_need_meaning)} words")
            auto_meanings = await self.dictionary_service.batch_get_definitions(
                list(set(words_need_meaning))
            )
        
        # Process entries
        for word, definition, example, line_num in parsed_entries:
            try:
                # Determine definition to use
                final_definition = definition
                meaning_source = MeaningSource.MANUAL
                is_auto = False
                
                if not final_definition and word in auto_meanings:
                    fetched_def, source = auto_meanings[word]
                    if fetched_def:
                        final_definition = fetched_def
                        meaning_source = source
                        is_auto = True
                        result.auto_generated_count += 1
                
                if not final_definition:
                    result.failed_auto_meaning.append(word)
                    result.warnings.append(f"Line {line_num}: No definition found for '{word}'")
                    # Vẫn tạo vocabulary nhưng không có meaning
                    self._create_or_merge_vocab(user_id, word, None, None, result)
                    continue
                
                # Create hoặc merge vocabulary
                self._create_or_merge_vocab(
                    user_id, word, final_definition, example,
                    result, meaning_source, is_auto
                )
                
            except Exception as e:
                result.errors.append(f"Line {line_num}: Error processing '{word}': {str(e)}")
                logger.error(f"Import error for word '{word}': {e}")
        
        # Commit tất cả changes
        self.session.commit()
        
        logger.info(
            f"Import completed: {result.total_processed} processed, "
            f"{result.new_words} new, {result.merged_meanings} merged, "
            f"{result.auto_generated_count} auto-generated"
        )
        
        return result
    
    def _create_or_merge_vocab(
        self,
        user_id: int,
        word: str,
        definition: Optional[str],
        example: Optional[str],
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
                        example_sentence=example,
                        meaning_source=source,
                        is_auto_generated=is_auto
                    )
                    self.session.add(meaning)
                    result.merged_meanings += 1
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
                    example_sentence=example,
                    meaning_source=source,
                    is_auto_generated=is_auto
                )
                self.session.add(meaning)
            
            result.new_words += 1
    
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
                        "example_sentence": m.example_sentence,
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
                if meaning.example_sentence:
                    parts.append(meaning.example_sentence)
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
                    meaning.example_sentence or "",
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
        review_data: VocabularyReview
    ) -> Optional[Vocabulary]:
        """
        Update learning status của vocabulary sau khi review (SRS algorithm).
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
            review_quality=quality
        )
        
        # Cập nhật lại model
        vocab.easiness_factor = new_srs_state.easiness_factor
        vocab.interval = new_srs_state.interval
        vocab.repetitions = new_srs_state.repetitions
        vocab.next_review_date = new_srs_state.next_review_date
        
        self.session.add(vocab)
        self.session.commit()
        self.session.refresh(vocab)
        
        logger.info(f"Updated SRS for vocab {vocab_id}: EF={vocab.easiness_factor:.2f}")
        
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
        query = select(Vocabulary).where(
            and_(
                Vocabulary.user_id == user_id,
                Vocabulary.next_review_date <= datetime.utcnow()
            )
        ).options(selectinload(Vocabulary.meanings)).order_by(
            Vocabulary.next_review_date.asc()
        ).limit(limit)
        
        due_vocabs = list(self.session.exec(query).all())
        
        if not due_vocabs:
            return QuizSessionResponse(questions=[])
        
        ai_provider = get_ai_provider()
        questions = []
        
        for vocab in due_vocabs:
            try:
                # Lấy definition đầu tiên cho quiz
                definition = vocab.meanings[0].definition if vocab.meanings else ""
                
                ai_q = await ai_provider.generate_question(
                    vocab=vocab,
                    practice_type=PracticeType.MULTIPLE_CHOICE
                )
                
                questions.append(QuizQuestion(
                    id=vocab.id,
                    word=vocab.word,
                    question_text=ai_q.question_text,
                    options=ai_q.options or {},
                    correct_answer=ai_q.correct_answer,
                    explanation=ai_q.explanation or "",
                    grammar_explanation=ai_q.grammar_explanation
                ))
            except Exception as e:
                logger.error(f"Error generating quiz for vocab {vocab.id}: {e}")
                continue
        
        return QuizSessionResponse(questions=questions)
