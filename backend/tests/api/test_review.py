"""Tests cho Review và SRS Integration."""
import pytest
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.vocabulary import Vocabulary
from app.models.review_history import ReviewHistory
from app.models.enums import ReviewQuality


def test_review_vocabulary_good(auth_client: TestClient, session: Session):
    """Test review từ vựng với chất lượng GOOD."""
    # Tạo từ vựng ban đầu
    create_res = auth_client.post("/api/v1/vocabulary/", json={
        "word": "SRS",
        "meanings": [{"definition": "Spaced Repetition System"}]
    })
    vocab_id = create_res.json()["id"]
    
    # Review lần 1 - GOOD
    review_data = {
        "review_quality": ReviewQuality.GOOD,
        "time_spent_seconds": 10
    }
    response = auth_client.post(f"/api/v1/vocabulary/{vocab_id}/review", json=review_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["repetitions"] == 1
    assert data["interval"] == 1
    
    # Kiểm tra database
    db_vocab = session.get(Vocabulary, vocab_id)
    assert db_vocab.repetitions == 1
    assert db_vocab.interval == 1
    assert db_vocab.next_review_date > datetime.utcnow()


def test_review_vocabulary_again_resets(auth_client: TestClient):
    """Test review AGAIN làm reset tiến trình."""
    # Tạo từ vựng đã có tiến trình
    create_res = auth_client.post("/api/v1/vocabulary/", json={
        "word": "Reset",
        "meanings": [{"definition": "To start over"}]
    })
    vocab_id = create_res.json()["id"]
    
    # Học lần 1
    auth_client.post(f"/api/v1/vocabulary/{vocab_id}/review", json={"review_quality": ReviewQuality.GOOD})
    
    # Quên (AGAIN)
    response = auth_client.post(f"/api/v1/vocabulary/{vocab_id}/review", json={"review_quality": ReviewQuality.AGAIN})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["repetitions"] == 0
    assert data["interval"] == 0


def test_submit_quiz_answer_single(auth_client: TestClient):
    """Test submit kết quả quiz đơn lẻ."""
    create_res = auth_client.post("/api/v1/vocabulary/", json={
        "word": "Quiz",
        "meanings": [{"definition": "A short test"}]
    })
    vocab_id = create_res.json()["id"]
    
    # Submit đúng
    submit_data = {
        "vocabulary_id": vocab_id,
        "is_correct": True,
        "time_spent_seconds": 5
    }
    response = auth_client.post("/api/v1/vocabulary/quiz-submit-single", json=submit_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["repetitions"] == 1
    
    # Submit sai
    submit_data["is_correct"] = False
    response = auth_client.post("/api/v1/vocabulary/quiz-submit-single", json=submit_data)
    assert response.json()["repetitions"] == 0


def test_review_history_created(auth_client: TestClient, session: Session, normal_user):
    """Test review history được lưu vào database."""
    create_res = auth_client.post("/api/v1/vocabulary/", json={
        "word": "History", 
        "meanings": [{"definition": "Past events"}]
    })
    vocab_id = create_res.json()["id"]
    
    auth_client.post(f"/api/v1/vocabulary/{vocab_id}/review", json={"review_quality": ReviewQuality.EASY})
    
    history = session.exec(select(ReviewHistory).where(ReviewHistory.vocabulary_id == vocab_id)).first()
    assert history is not None
    assert history.review_quality == ReviewQuality.EASY
    assert history.user_id == normal_user.id
