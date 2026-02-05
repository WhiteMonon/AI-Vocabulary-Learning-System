"""
Vocabulary Service Layer - Business logic cho vocabulary management và SRS.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlmodel import Session, select, func, and_
from sqlalchemy.exc import IntegrityError

from app.models.vocabulary import Vocabulary
from app.models.review_history import ReviewHistory
from app.models.enums import ReviewQuality, DifficultyLevel
from app.schemas.vocabulary import (
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyReview,
    VocabularyStatsResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class VocabularyService:
    """
    Service layer cho vocabulary management.
    Implement business logic cho CRUD operations và SRS algorithm.
    """
    
    def __init__(self, session: Session):
        """
        Initialize vocabulary service.
        
        Args:
            session: Database session (không phải FastAPI request)
        """
        self.session = session
    
    def create_vocab(
        self,
        user_id: int,
        vocab_data: VocabularyCreate
    ) -> Vocabulary:
        """
        Tạo vocabulary mới cho user.
        
        Args:
            user_id: ID của user
            vocab_data: Data để tạo vocabulary
            
        Returns:
            Vocabulary đã được tạo
            
        Raises:
            ValueError: Nếu vocabulary đã tồn tại cho user
        """
        try:
            # Tạo vocabulary với SRS defaults
            vocab = Vocabulary(
                user_id=user_id,
                word=vocab_data.word,
                definition=vocab_data.definition,
                example_sentence=vocab_data.example_sentence,
                difficulty_level=vocab_data.difficulty_level,
                # SRS defaults
                easiness_factor=2.5,
                interval=0,
                repetitions=0,
                next_review_date=datetime.utcnow()  # Có thể review ngay
            )
            
            self.session.add(vocab)
            self.session.commit()
            self.session.refresh(vocab)
            
            logger.info(f"Created vocabulary '{vocab.word}' for user {user_id}")
            return vocab
            
        except IntegrityError as e:
            self.session.rollback()
            logger.warning(f"Vocabulary '{vocab_data.word}' already exists for user {user_id}")
            raise ValueError(f"Vocabulary '{vocab_data.word}' đã tồn tại") from e
    
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
            user_id: ID của user (để verify ownership)
            vocab_data: Data để update
            
        Returns:
            Vocabulary đã được update, hoặc None nếu không tìm thấy
        """
        # Tìm vocabulary và verify ownership
        vocab = self.session.get(Vocabulary, vocab_id)
        if not vocab or vocab.user_id != user_id:
            logger.warning(f"Vocabulary {vocab_id} not found for user {user_id}")
            return None
        
        # Update các fields được cung cấp
        update_data = vocab_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vocab, field, value)
        
        try:
            self.session.add(vocab)
            self.session.commit()
            self.session.refresh(vocab)
            
            logger.info(f"Updated vocabulary {vocab_id} for user {user_id}")
            return vocab
            
        except IntegrityError as e:
            self.session.rollback()
            logger.warning(f"Update failed - word conflict for user {user_id}")
            raise ValueError(f"Vocabulary '{vocab_data.word}' đã tồn tại") from e
    
    def delete_vocab(
        self,
        vocab_id: int,
        user_id: int
    ) -> bool:
        """
        Xóa vocabulary của user.
        
        Args:
            vocab_id: ID của vocabulary
            user_id: ID của user (để verify ownership)
            
        Returns:
            True nếu xóa thành công, False nếu không tìm thấy
        """
        vocab = self.session.get(Vocabulary, vocab_id)
        if not vocab or vocab.user_id != user_id:
            logger.warning(f"Vocabulary {vocab_id} not found for user {user_id}")
            return False
        
        self.session.delete(vocab)
        self.session.commit()
        
        logger.info(f"Deleted vocabulary {vocab_id} for user {user_id}")
        return True
    
    def get_vocab_list(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        difficulty: Optional[DifficultyLevel] = None,
        due_only: bool = False,
        search: Optional[str] = None
    ) -> tuple[List[Vocabulary], int]:
        """
        Lấy danh sách vocabularies của user với filters.
        
        Args:
            user_id: ID của user
            skip: Số lượng records để skip (pagination)
            limit: Số lượng records tối đa trả về
            difficulty: Filter theo difficulty level
            due_only: Chỉ lấy vocabularies cần review hôm nay
            search: Tìm kiếm theo word hoặc definition
            
        Returns:
            Tuple (danh sách vocabularies, tổng số records)
        """
        # Base query
        query = select(Vocabulary).where(Vocabulary.user_id == user_id)
        
        # Apply filters
        if difficulty:
            query = query.where(Vocabulary.difficulty_level == difficulty)
        
        if due_only:
            query = query.where(Vocabulary.next_review_date <= datetime.utcnow())
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Vocabulary.word.ilike(search_pattern)) |
                (Vocabulary.definition.ilike(search_pattern))
            )
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.exec(count_query).one()
        
        # Apply pagination và order
        query = query.order_by(Vocabulary.next_review_date.asc()).offset(skip).limit(limit)
        
        # Execute
        vocabularies = self.session.exec(query).all()
        
        logger.info(f"Retrieved {len(vocabularies)} vocabularies for user {user_id} (total: {total})")
        return list(vocabularies), total
    
    def update_learning_status(
        self,
        vocab_id: int,
        user_id: int,
        review_data: VocabularyReview
    ) -> Optional[Vocabulary]:
        """
        Update learning status của vocabulary sau khi review (SRS algorithm).
        Implement SM-2 (SuperMemo 2) algorithm.
        
        Args:
            vocab_id: ID của vocabulary
            user_id: ID của user (để verify ownership)
            review_data: Review quality và time spent
            
        Returns:
            Vocabulary đã được update, hoặc None nếu không tìm thấy
        """
        vocab = self.session.get(Vocabulary, vocab_id)
        if not vocab or vocab.user_id != user_id:
            logger.warning(f"Vocabulary {vocab_id} not found for user {user_id}")
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
        
        # Apply SM-2 algorithm
        quality = review_data.review_quality.value
        
        # Update easiness factor
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        ef = vocab.easiness_factor
        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ef = max(1.3, ef)  # Minimum EF = 1.3
        vocab.easiness_factor = ef
        
        # Update repetitions và interval
        if quality < 3:  # AGAIN hoặc HARD
            # Reset về đầu
            vocab.repetitions = 0
            vocab.interval = 0
            vocab.next_review_date = datetime.utcnow()  # Review lại ngay
        else:  # GOOD hoặc EASY
            vocab.repetitions += 1
            
            if vocab.repetitions == 1:
                vocab.interval = 1
            elif vocab.repetitions == 2:
                vocab.interval = 6
            else:
                vocab.interval = round(vocab.interval * ef)
            
            # Calculate next review date
            vocab.next_review_date = datetime.utcnow() + timedelta(days=vocab.interval)
        
        self.session.add(vocab)
        self.session.commit()
        self.session.refresh(vocab)
        
        logger.info(
            f"Updated learning status for vocab {vocab_id}: "
            f"quality={quality}, EF={ef:.2f}, interval={vocab.interval}, "
            f"next_review={vocab.next_review_date.date()}"
        )
        
        return vocab
    
    def get_vocab_stats(self, user_id: int) -> VocabularyStatsResponse:
        """
        Lấy thống kê vocabularies của user.
        
        Args:
            user_id: ID của user
            
        Returns:
            Statistics về vocabularies
        """
        # Total vocabularies
        total_query = select(func.count()).select_from(Vocabulary).where(
            Vocabulary.user_id == user_id
        )
        total = self.session.exec(total_query).one()
        
        # Due today
        due_query = select(func.count()).select_from(Vocabulary).where(
            and_(
                Vocabulary.user_id == user_id,
                Vocabulary.next_review_date <= datetime.utcnow()
            )
        )
        due_today = self.session.exec(due_query).one()
        
        # Learned (repetitions > 0)
        learned_query = select(func.count()).select_from(Vocabulary).where(
            and_(
                Vocabulary.user_id == user_id,
                Vocabulary.repetitions > 0
            )
        )
        learned = self.session.exec(learned_query).one()
        
        # Learning (repetitions == 0)
        learning = total - learned
        
        # By difficulty
        by_difficulty = {}
        for difficulty in DifficultyLevel:
            diff_query = select(func.count()).select_from(Vocabulary).where(
                and_(
                    Vocabulary.user_id == user_id,
                    Vocabulary.difficulty_level == difficulty
                )
            )
            count = self.session.exec(diff_query).one()
            by_difficulty[difficulty.value] = count
        
        return VocabularyStatsResponse(
            total_vocabularies=total,
            due_today=due_today,
            learned=learned,
            learning=learning,
            by_difficulty=by_difficulty
        )
