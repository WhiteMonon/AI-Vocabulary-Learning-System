"""
Vocabulary API Router - Các endpoints quản lý từ vựng.
Updated để hỗ trợ multiple meanings và import/export.
"""
import json
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import PlainTextResponse, StreamingResponse
from sqlmodel import Session

from app.api import deps
from app.models.user import User
from app.models.enums import WordType, ReviewQuality, MeaningSource
from app.schemas.vocabulary import (
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyReview,
    VocabularyResponse,
    VocabularyListResponse,
    VocabularyStatsResponse,
    MeaningCreate,
    MeaningResponse,
    VocabularyImportRequest,
    ImportResultResponse
)
from app.schemas.quiz import QuizSessionResponse, QuizSubmit
from app.services.vocabulary_service import VocabularyService

router = APIRouter()


# ============= Import/Export Endpoints =============

@router.post("/import", response_model=ImportResultResponse)
async def import_vocabularies(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    import_data: VocabularyImportRequest
):
    """
    Import từ vựng từ nội dung TXT.
    
    Format mỗi dòng: word|definition|example (definition và example optional)
    
    Nếu word đã tồn tại, sẽ merge thêm meaning mới.
    Nếu không có definition và auto_fetch_meaning=True, sẽ tự động fetch từ API.
    """
    service = VocabularyService(db)
    result = await service.import_from_txt(
        user_id=current_user.id,
        content=import_data.content,
        auto_fetch_meaning=import_data.auto_fetch_meaning
    )
    
    return ImportResultResponse(
        total_processed=result.total_processed,
        new_words=result.new_words,
        merged_meanings=result.merged_meanings,
        auto_generated_count=result.auto_generated_count,
        failed_auto_meaning=result.failed_auto_meaning,
        warnings=result.warnings,
        errors=result.errors
    )


@router.post("/import-stream")
async def import_vocabularies_stream(
    *,
    current_user: User = Depends(deps.get_current_user),
    import_data: VocabularyImportRequest
):
    """
    Import từ vựng với streaming progress updates (SSE).
    
    Endpoint này sử dụng Server-Sent Events để gửi real-time progress updates.
    
    Events:
    - progress: {"type": "progress", "data": {"current": N, "total": M, "percent": X}}
    - item_processed: {"type": "item_processed", "data": {"word": "...", "status": "success|failed|warning", "message": "..."}}
    - completed: {"type": "completed", "data": ImportResult}
    """
    # Lưu user_id trước khi vào generator (tránh detached session)
    user_id = current_user.id
    content = import_data.content
    auto_fetch = import_data.auto_fetch_meaning
    
    async def event_generator():
        """Generator để format events cho SSE với session riêng."""
        from app.db.session import engine
        from sqlmodel import Session
        
        # Tạo session mới trong generator
        db = Session(engine)
        try:
            service = VocabularyService(db)
            
            async for event in service.import_from_txt_stream(
                user_id=user_id,
                content=content,
                auto_fetch_meaning=auto_fetch
            ):
                # Format SSE event
                event_type = event.get("type", "message")
                event_data = json.dumps(event.get("data", {}), ensure_ascii=False)
                
                # SSE format: event: <type>\ndata: <json>\n\n
                yield f"event: {event_type}\n"
                yield f"data: {event_data}\n\n"
                
        except Exception as e:
            # Send error event
            error_data = json.dumps({"message": str(e)}, ensure_ascii=False)
            yield f"event: error\n"
            yield f"data: {error_data}\n\n"
        finally:
            # Đảm bảo đóng session
            db.close()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )



@router.get("/export")
def export_vocabularies(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    format: Literal["json", "txt", "csv"] = Query("json", description="Format export"),
    page: Optional[int] = Query(None, ge=1, description="Page number (optional, None = all)")
):
    """
    Export từ vựng của user theo format được chọn.
    
    - **json**: JSON với đầy đủ thông tin
    - **txt**: word|definition|example (mỗi dòng một meaning)
    - **csv**: CSV với header
    """
    service = VocabularyService(db)
    content = service.export_vocabularies(
        user_id=current_user.id,
        format=format,
        page=page
    )
    
    # Set appropriate content type
    if format == "json":
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=vocabularies.json"}
        )
    elif format == "csv":
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=vocabularies.csv"}
        )
    else:  # txt
        return PlainTextResponse(
            content=content,
            headers={"Content-Disposition": "attachment; filename=vocabularies.txt"}
        )


# ============= CRUD Endpoints =============

@router.post("/", response_model=VocabularyResponse, status_code=status.HTTP_201_CREATED)
def create_vocabulary(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    vocab_in: VocabularyCreate
):
    """
    Tạo một từ vựng mới cho người dùng hiện tại.
    
    Word sẽ được tự động normalize (lowercase, trim).
    Word type sẽ được tự động classify nếu không chỉ định.
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
    word_type: Optional[WordType] = Query(None, description="Filter theo word type"),
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
        word_type=word_type,
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


@router.get("/quiz-session", response_model=QuizSessionResponse)
async def get_quiz_session(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    limit: int = Query(10, ge=1, le=20)
):
    """
    Tạo một phiên quiz trắc nghiệm (AI-powered) cho người dùng.
    """
    service = VocabularyService(db)
    return await service.generate_quiz_session(user_id=current_user.id, limit=limit)


@router.post("/quiz-submit-single", response_model=VocabularyResponse)
def submit_quiz_answer(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    submit_in: QuizSubmit
):
    """
    Submit kết quả của một câu hỏi quiz.
    """
    service = VocabularyService(db)
    
    quality = ReviewQuality.GOOD if submit_in.is_correct else ReviewQuality.AGAIN
    
    review_data = VocabularyReview(
        review_quality=quality,
        time_spent_seconds=submit_in.time_spent_seconds
    )
    
    vocab = service.update_learning_status(
        vocab_id=submit_in.vocabulary_id,
        user_id=current_user.id,
        review_data=review_data
    )
    
    if not vocab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy từ vựng"
        )
    return vocab


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
    try:
        vocab = service.update_vocab(vocab_id=id, user_id=current_user.id, vocab_data=vocab_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
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


# ============= Meaning Endpoints =============

@router.post("/{id}/meanings", response_model=MeaningResponse, status_code=status.HTTP_201_CREATED)
def add_meaning(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    meaning_in: MeaningCreate
):
    """
    Thêm meaning mới cho vocabulary.
    
    Duplicate meanings sẽ bị bỏ qua.
    """
    service = VocabularyService(db)
    meaning = service.add_meaning(
        vocab_id=id,
        user_id=current_user.id,
        meaning_data=meaning_in,
        source=MeaningSource.MANUAL,
        is_auto=False
    )
    
    if not meaning:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tìm thấy từ vựng hoặc meaning đã tồn tại"
        )
    return meaning
