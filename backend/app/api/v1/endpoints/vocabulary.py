"""
Vocabulary API Router - Các endpoints quản lý từ vựng.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api import deps
from app.models.user import User
from app.models.enums import DifficultyLevel
from app.schemas.vocabulary import (
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyReview,
    VocabularyResponse,
    VocabularyListResponse,
    VocabularyStatsResponse
)
from app.services.vocabulary_service import VocabularyService

router = APIRouter()


@router.post("/", response_model=VocabularyResponse, status_code=status.HTTP_201_CREATED)
def create_vocabulary(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    vocab_in: VocabularyCreate
):
    """
    Tạo một từ vựng mới cho người dùng hiện tại.
    """
    service = VocabularyService(db)
    try:
        return service.create_vocab(user_id=current_user.id, vocab_data=vocab_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=VocabularyListResponse)
def list_vocabularies(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    difficulty: Optional[DifficultyLevel] = None,
    status: Optional[str] = Query(None, description="Trạng thái: LEARNED, LEARNING, DUE"),
    search: Optional[str] = None
):
    """
    Lấy danh sách từ vựng với phân trang, lọc và tìm kiếm.
    """
    service = VocabularyService(db)
    skip = (page - 1) * page_size
    items, total = service.get_vocab_list(
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        difficulty=difficulty,
        status=status,
        search=search
    )
    
    total_pages = (total + page_size - 1) // page_size
    return VocabularyListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/stats", response_model=VocabularyStatsResponse)
def get_vocabulary_stats(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Lấy thống kê từ vựng của người dùng hiện tại.
    """
    service = VocabularyService(db)
    return service.get_vocab_stats(user_id=current_user.id)


@router.get("/{id}", response_model=VocabularyResponse)
def get_vocabulary(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
):
    """
    Lấy thông tin chi tiết của một từ vựng theo ID.
    """
    service = VocabularyService(db)
    vocab = service.get_vocab(vocab_id=id, user_id=current_user.id)
    if not vocab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy từ vựng"
        )
    return vocab


@router.patch("/{id}", response_model=VocabularyResponse)
def update_vocabulary(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    vocab_in: VocabularyUpdate
):
    """
    Cập nhật thông tin từ vựng.
    """
    service = VocabularyService(db)
    vocab = service.update_vocab(vocab_id=id, user_id=current_user.id, vocab_data=vocab_in)
    if not vocab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy từ vựng"
        )
    return vocab


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vocabulary(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
):
    """
    Xóa một từ vựng.
    """
    service = VocabularyService(db)
    success = service.delete_vocab(vocab_id=id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy từ vựng"
        )
    return None


@router.post("/{id}/review", response_model=VocabularyResponse)
def review_vocabulary(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    review_in: VocabularyReview
):
    """
    Cập nhật trạng thái học tập của từ vựng sau khi review (SRS).
    """
    service = VocabularyService(db)
    vocab = service.update_learning_status(
        vocab_id=id, 
        user_id=current_user.id, 
        review_data=review_in
    )
    if not vocab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy từ vựng"
        )
    return vocab
