"""
Review API endpoints - Context-based review với question snapshots.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_session
from app.models.user import User
from app.models.review_session import ReviewSession
from app.models.generated_question import GeneratedQuestion
from app.schemas.review import (
    ReviewSessionCreate,
    ReviewSessionResponse,
    QuestionResponse,
    QuestionSubmission,
    BatchSubmitRequest,
    SubmitResponse,
    BatchSubmitResponse,
    SessionSummaryResponse,
)
from app.services.review_service import ReviewService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/sessions", response_model=ReviewSessionResponse, status_code=status.HTTP_201_CREATED)
def create_review_session(
    *,
    session_data: ReviewSessionCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo review session mới với generated questions.
    
    - **mode**: 'due' (cần ôn) hoặc 'new' (từ mới)
    - **max_questions**: Số câu hỏi tối đa (default 20)
    
    Returns:
        ReviewSession với danh sách questions (snapshots)
    """
    review_service = ReviewService(db)
    
    # Create session
    review_session = review_service.create_session(
        user_id=current_user.id,
        mode=session_data.mode,
        max_questions=session_data.max_questions
    )
    
    # Load questions
    db.refresh(review_session)
    query = db.query(ReviewSession).filter(
        ReviewSession.id == review_session.id
    ).options(selectinload(ReviewSession.questions))
    review_session = query.first()
    
    # Map to response
    questions_response = [
        QuestionResponse(
            question_instance_id=q.question_instance_id,
            vocabulary_id=q.vocabulary_id,
            question_type=q.question_type,
            difficulty=q.difficulty,
            question_text=q.question_data.get("question_text", ""),
            options=q.question_data.get("options"),
            context_sentence=q.question_data.get("context_sentence"),
            confusion_pair_group=q.confusion_pair_group,
        )
        for q in review_session.questions
    ]
    
    response = ReviewSessionResponse(
        session_id=review_session.id,
        status=review_session.status,
        total_questions=review_session.total_questions,
        questions=questions_response,
        started_at=review_session.started_at,
    )
    
    logger.info(f"Created review session {review_session.id} for user {current_user.id}")
    return response


@router.post("/sessions/{session_id}/submit", response_model=BatchSubmitResponse)
def submit_answers(
    *,
    session_id: int,
    submit_data: BatchSubmitRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Submit batch answers cho review session.
    
    - **submissions**: Danh sách câu trả lời với telemetry data
    
    Returns:
        Kết quả evaluation cho từng câu hỏi và session summary
    """
    review_service = ReviewService(db)
    
    # Verify session belongs to user
    review_session = db.get(ReviewSession, session_id)
    if not review_session or review_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Submit từng answer
    results = []
    for submission in submit_data.submissions:
        try:
            result = review_service.submit_answer(
                question_instance_id=submission.question_instance_id,
                user_answer=submission.user_answer,
                time_spent_ms=submission.time_spent_ms,
                answer_change_count=submission.answer_change_count
            )
            results.append(SubmitResponse(**result))
        except ValueError as e:
            logger.error(f"Error submitting answer: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # Complete session và update SRS
    summary = review_service.complete_session(session_id)
    
    response = BatchSubmitResponse(
        results=results,
        session_summary=summary
    )
    
    logger.info(f"Completed session {session_id} for user {current_user.id}")
    return response


@router.get("/sessions/{session_id}", response_model=ReviewSessionResponse)
def get_review_session(
    *,
    session_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết của review session.
    """
    query = db.query(ReviewSession).filter(
        ReviewSession.id == session_id,
        ReviewSession.user_id == current_user.id
    ).options(selectinload(ReviewSession.questions))
    
    review_session = query.first()
    
    if not review_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Map to response
    questions_response = [
        QuestionResponse(
            question_instance_id=q.question_instance_id,
            vocabulary_id=q.vocabulary_id,
            question_type=q.question_type,
            difficulty=q.difficulty,
            question_text=q.question_data.get("question_text", ""),
            options=q.question_data.get("options"),
            context_sentence=q.question_data.get("context_sentence"),
            confusion_pair_group=q.confusion_pair_group,
        )
        for q in review_session.questions
    ]
    
    response = ReviewSessionResponse(
        session_id=review_session.id,
        status=review_session.status,
        total_questions=review_session.total_questions,
        questions=questions_response,
        started_at=review_session.started_at,
    )
    
    return response
