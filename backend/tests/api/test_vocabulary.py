"""Tests cho Vocabulary CRUD API."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.vocabulary import Vocabulary
from app.models.vocabulary_meaning import VocabularyMeaning
from app.models.enums import WordType


def test_create_vocabulary(auth_client: TestClient, session: Session):
    """Test tạo mới một từ vựng với meanings."""
    vocab_data = {
        "word": "Hello",
        "meanings": [
            {
                "definition": "A greeting",
                "example_sentence": "Hello, how are you?"
            }
        ],
        "word_type": "content_word"
    }
    response = auth_client.post("/api/v1/vocabulary/", json=vocab_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["word"] == "hello"  # Normalized
    assert len(data["meanings"]) == 1
    assert data["meanings"][0]["definition"] == "A greeting"
    assert "id" in data
    
    # Kiểm tra database
    statement = select(Vocabulary).where(Vocabulary.word == "hello").options(selectinload(Vocabulary.meanings))
    db_vocab = session.exec(statement).first()
    assert db_vocab is not None
    assert len(db_vocab.meanings) == 1
    assert db_vocab.meanings[0].definition == "A greeting"


def test_create_duplicate_vocabulary(auth_client: TestClient):
    """Test không cho phép tạo từ vựng trùng lặp cho cùng một user."""
    vocab_data = {
        "word": "World",
        "meanings": [{"definition": "The Earth"}]
    }
    # Tạo lần 1
    auth_client.post("/api/v1/vocabulary/", json=vocab_data)
    # Tạo lần 2
    response = auth_client.post("/api/v1/vocabulary/", json=vocab_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "đã tồn tại" in response.json()["detail"]


def test_list_vocabularies(auth_client: TestClient, normal_user):
    """Test lấy danh sách từ vựng."""
    # Thêm data mẫu trực tiếp vào API
    auth_client.post("/api/v1/vocabulary/", json={
        "word": "Apple", 
        "meanings": [{"definition": "A fruit"}]
    })
    auth_client.post("/api/v1/vocabulary/", json={
        "word": "Banana", 
        "meanings": [{"definition": "Another fruit"}]
    })
    
    response = auth_client.get("/api/v1/vocabulary/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_get_vocabulary(auth_client: TestClient):
    """Test lấy chi tiết một từ vựng."""
    create_res = auth_client.post("/api/v1/vocabulary/", json={
        "word": "Test", 
        "meanings": [{"definition": "Testing"}]
    })
    vocab_id = create_res.json()["id"]
    
    response = auth_client.get(f"/api/v1/vocabulary/{vocab_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["word"] == "test"


def test_update_vocabulary(auth_client: TestClient):
    """Test cập nhật từ vựng (chỉ update word/word_type)."""
    create_res = auth_client.post("/api/v1/vocabulary/", json={
        "word": "Old", 
        "meanings": [{"definition": "Old meaning"}]
    })
    vocab_id = create_res.json()["id"]
    
    update_data = {"word": "New Word", "word_type": "function_word"}
    response = auth_client.patch(f"/api/v1/vocabulary/{vocab_id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["word"] == "new word"
    assert response.json()["word_type"] == "function_word"


def test_add_meaning(auth_client: TestClient):
    """Test thêm meaning cho từ vựng đã có."""
    create_res = auth_client.post("/api/v1/vocabulary/", json={
        "word": "Bank", 
        "meanings": [{"definition": "A financial institution"}]
    })
    vocab_id = create_res.json()["id"]
    
    meaning_data = {"definition": "The land alongside a river"}
    response = auth_client.post(f"/api/v1/vocabulary/{vocab_id}/meanings", json=meaning_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["definition"] == "The land alongside a river"
    
    # Check lại vocab
    get_res = auth_client.get(f"/api/v1/vocabulary/{vocab_id}")
    assert len(get_res.json()["meanings"]) == 2


def test_delete_vocabulary(auth_client: TestClient, session: Session):
    """Test xóa một từ vựng."""
    create_res = auth_client.post("/api/v1/vocabulary/", json={
        "word": "DeleteMe", 
        "meanings": [{"definition": "To be deleted"}]
    })
    vocab_id = create_res.json()["id"]
    
    response = auth_client.delete(f"/api/v1/vocabulary/{vocab_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Kiểm tra database đã xóa
    db_vocab = session.get(Vocabulary, vocab_id)
    assert db_vocab is None


def test_get_vocabulary_stats(auth_client: TestClient):
    """Test lấy thống kê từ vựng."""
    # Đảm bảo có ít nhất 1 từ vựng
    auth_client.post("/api/v1/vocabulary/", json={
        "word": "StatsTest", 
        "meanings": [{"definition": "For stats"}]
    })
    
    response = auth_client.get("/api/v1/vocabulary/stats")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_vocabularies" in data
    assert "by_word_type" in data
