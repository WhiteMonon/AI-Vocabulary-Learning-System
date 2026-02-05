"""
Example usage của VocabularyService.
File này minh họa cách sử dụng service layer trong API endpoints.
"""
from sqlmodel import Session
from app.services.vocabulary_service import VocabularyService
from app.schemas.vocabulary import (
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyReview
)
from app.models.enums import DifficultyLevel, ReviewQuality


# ============= Example 1: Tạo vocabulary mới =============

def example_create_vocabulary(session: Session, user_id: int):
    """Example: Tạo vocabulary mới."""
    service = VocabularyService(session)
    
    vocab_data = VocabularyCreate(
        word="serendipity",
        definition="The occurrence of events by chance in a happy or beneficial way",
        example_sentence="Finding that book was pure serendipity.",
        difficulty_level=DifficultyLevel.HARD
    )
    
    try:
        vocab = service.create_vocab(user_id=user_id, vocab_data=vocab_data)
        print(f"Created vocabulary: {vocab.word} (ID: {vocab.id})")
        print(f"Next review: {vocab.next_review_date}")
        return vocab
    except ValueError as e:
        print(f"Error: {e}")
        return None


# ============= Example 2: Update vocabulary =============

def example_update_vocabulary(session: Session, vocab_id: int, user_id: int):
    """Example: Update vocabulary."""
    service = VocabularyService(session)
    
    update_data = VocabularyUpdate(
        definition="Updated definition: The occurrence and development of events by chance",
        example_sentence="It was serendipity that we met at the conference."
    )
    
    vocab = service.update_vocab(
        vocab_id=vocab_id,
        user_id=user_id,
        vocab_data=update_data
    )
    
    if vocab:
        print(f"Updated vocabulary: {vocab.word}")
        return vocab
    else:
        print("Vocabulary not found or access denied")
        return None


# ============= Example 3: Get vocabulary list với filters =============

def example_get_vocabulary_list(session: Session, user_id: int):
    """Example: Lấy danh sách vocabularies với filters."""
    service = VocabularyService(session)
    
    # Lấy tất cả vocabularies cần review hôm nay
    vocabularies, total = service.get_vocab_list(
        user_id=user_id,
        skip=0,
        limit=20,
        due_only=True  # Chỉ lấy vocabularies cần review
    )
    
    print(f"Found {total} vocabularies due for review")
    for vocab in vocabularies:
        print(f"- {vocab.word}: next review {vocab.next_review_date}")
    
    # Lấy vocabularies theo difficulty
    hard_vocabs, hard_total = service.get_vocab_list(
        user_id=user_id,
        difficulty=DifficultyLevel.HARD,
        skip=0,
        limit=10
    )
    
    print(f"\nFound {hard_total} HARD vocabularies")
    
    # Search vocabularies
    search_results, search_total = service.get_vocab_list(
        user_id=user_id,
        search="serendipity",
        skip=0,
        limit=10
    )
    
    print(f"\nSearch results: {search_total} matches")
    
    return vocabularies


# ============= Example 4: Review vocabulary (SRS update) =============

def example_review_vocabulary(session: Session, vocab_id: int, user_id: int):
    """Example: Review vocabulary và update SRS status."""
    service = VocabularyService(session)
    
    # User review với quality GOOD
    review_data = VocabularyReview(
        review_quality=ReviewQuality.GOOD,
        time_spent_seconds=45
    )
    
    vocab = service.update_learning_status(
        vocab_id=vocab_id,
        user_id=user_id,
        review_data=review_data
    )
    
    if vocab:
        print(f"Reviewed vocabulary: {vocab.word}")
        print(f"Easiness Factor: {vocab.easiness_factor:.2f}")
        print(f"Interval: {vocab.interval} days")
        print(f"Repetitions: {vocab.repetitions}")
        print(f"Next review: {vocab.next_review_date}")
        return vocab
    else:
        print("Vocabulary not found")
        return None


# ============= Example 5: Review với different qualities =============

def example_review_scenarios(session: Session, vocab_id: int, user_id: int):
    """Example: Các scenarios review khác nhau."""
    service = VocabularyService(session)
    
    # Scenario 1: User quên hoàn toàn (AGAIN)
    print("Scenario 1: User forgot the word")
    review_again = VocabularyReview(
        review_quality=ReviewQuality.AGAIN,
        time_spent_seconds=60
    )
    vocab = service.update_learning_status(vocab_id, user_id, review_again)
    print(f"After AGAIN: interval={vocab.interval}, next_review={vocab.next_review_date}")
    
    # Scenario 2: User nhớ khó khăn (HARD)
    print("\nScenario 2: User remembered with difficulty")
    review_hard = VocabularyReview(
        review_quality=ReviewQuality.HARD,
        time_spent_seconds=30
    )
    vocab = service.update_learning_status(vocab_id, user_id, review_hard)
    print(f"After HARD: interval={vocab.interval}, next_review={vocab.next_review_date}")
    
    # Scenario 3: User nhớ tốt (GOOD)
    print("\nScenario 3: User remembered well")
    review_good = VocabularyReview(
        review_quality=ReviewQuality.GOOD,
        time_spent_seconds=20
    )
    vocab = service.update_learning_status(vocab_id, user_id, review_good)
    print(f"After GOOD: interval={vocab.interval}, next_review={vocab.next_review_date}")
    
    # Scenario 4: User nhớ rất dễ (EASY)
    print("\nScenario 4: User remembered easily")
    review_easy = VocabularyReview(
        review_quality=ReviewQuality.EASY,
        time_spent_seconds=10
    )
    vocab = service.update_learning_status(vocab_id, user_id, review_easy)
    print(f"After EASY: interval={vocab.interval}, next_review={vocab.next_review_date}")


# ============= Example 6: Get statistics =============

def example_get_statistics(session: Session, user_id: int):
    """Example: Lấy thống kê vocabularies."""
    service = VocabularyService(session)
    
    stats = service.get_vocab_stats(user_id=user_id)
    
    print("Vocabulary Statistics:")
    print(f"Total vocabularies: {stats.total_vocabularies}")
    print(f"Due today: {stats.due_today}")
    print(f"Learned (repetitions > 0): {stats.learned}")
    print(f"Learning (repetitions == 0): {stats.learning}")
    print("\nBy difficulty:")
    for difficulty, count in stats.by_difficulty.items():
        print(f"  {difficulty}: {count}")
    
    return stats


# ============= Example 7: Delete vocabulary =============

def example_delete_vocabulary(session: Session, vocab_id: int, user_id: int):
    """Example: Xóa vocabulary."""
    service = VocabularyService(session)
    
    success = service.delete_vocab(vocab_id=vocab_id, user_id=user_id)
    
    if success:
        print(f"Deleted vocabulary {vocab_id}")
    else:
        print("Vocabulary not found or access denied")
    
    return success


# ============= Example 8: Sử dụng trong FastAPI endpoint =============

"""
Example FastAPI endpoint sử dụng VocabularyService:

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.db.session import get_session
from app.services.vocabulary_service import VocabularyService
from app.schemas.vocabulary import VocabularyCreate, VocabularyResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/vocabularies", response_model=VocabularyResponse, status_code=status.HTTP_201_CREATED)
def create_vocabulary(
    vocab_data: VocabularyCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    '''Tạo vocabulary mới cho current user.'''
    service = VocabularyService(session)
    
    try:
        vocab = service.create_vocab(
            user_id=current_user.id,
            vocab_data=vocab_data
        )
        return vocab
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/vocabularies", response_model=VocabularyListResponse)
def get_vocabularies(
    skip: int = 0,
    limit: int = 100,
    difficulty: Optional[DifficultyLevel] = None,
    due_only: bool = False,
    search: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    '''Lấy danh sách vocabularies của current user.'''
    service = VocabularyService(session)
    
    vocabularies, total = service.get_vocab_list(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        difficulty=difficulty,
        due_only=due_only,
        search=search
    )
    
    total_pages = (total + limit - 1) // limit
    
    return VocabularyListResponse(
        items=vocabularies,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=total_pages
    )


@router.post("/vocabularies/{vocab_id}/review", response_model=VocabularyResponse)
def review_vocabulary(
    vocab_id: int,
    review_data: VocabularyReview,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    '''Review vocabulary và update SRS status.'''
    service = VocabularyService(session)
    
    vocab = service.update_learning_status(
        vocab_id=vocab_id,
        user_id=current_user.id,
        review_data=review_data
    )
    
    if not vocab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary not found"
        )
    
    return vocab
"""
