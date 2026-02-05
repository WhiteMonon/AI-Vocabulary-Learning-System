"""Tests cho Vocabulary CRUD API."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.user import User
from app.models.vocabulary import Vocabulary
from app.models.enums import DifficultyLevel



def test_create_vocabulary(auth_client: TestClient, session: Session):
    """Test tạo mới một từ vựng."""
    vocab_data = {
        "word": "Hello",
        "definition": "A greeting",
        "example_sentence": "Hello, how are you?",
        "difficulty_level": "medium"
    }
    response = auth_client.post("/api/v1/vocabulary/", json=vocab_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["word"] == "Hello"
    assert data["definition"] == "A greeting"
    assert "id" in data
    
    # Kiểm tra database
    db_vocab = session.exec(select(Vocabulary).where(Vocabulary.word == "Hello")).first()
    assert db_vocab is not None
    assert db_vocab.definition == "A greeting"


def test_create_duplicate_vocabulary(auth_client: TestClient):
    """Test không cho phép tạo từ vựng trùng lặp cho cùng một user."""
    vocab_data = {
        "word": "World",
        "definition": "The Earth",
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
    auth_client.post("/api/v1/vocabulary/", json={"word": "Apple", "definition": "A fruit"})
    auth_client.post("/api/v1/vocabulary/", json={"word": "Banana", "definition": "Another fruit"})
    
    response = auth_client.get("/api/v1/vocabulary/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_get_vocabulary(auth_client: TestClient):
    """Test lấy chi tiết một từ vựng."""
    # Tạo tạo 
    create_res = auth_client.post("/api/v1/vocabulary/", json={"word": "Test", "definition": "Testing"})
    vocab_id = create_res.json()["id"]
    
    response = auth_client.get(f"/api/v1/vocabulary/{vocab_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["word"] == "Test"


def test_update_vocabulary(auth_client: TestClient):
    """Test cập nhật từ vựng."""
    create_res = auth_client.post("/api/v1/vocabulary/", json={"word": "Old", "definition": "Old meaning"})
    vocab_id = create_res.json()["id"]
    
    update_data = {"definition": "New meaning", "difficulty_level": "easy"}
    response = auth_client.patch(f"/api/v1/vocabulary/{vocab_id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["definition"] == "New meaning"
    assert response.json()["difficulty_level"] == "easy"


def test_delete_vocabulary(auth_client: TestClient, session: Session):
    """Test xóa một từ vựng."""
    create_res = auth_client.post("/api/v1/vocabulary/", json={"word": "DeleteMe", "definition": "To be deleted"})
    vocab_id = create_res.json()["id"]
    
    response = auth_client.delete(f"/api/v1/vocabulary/{vocab_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Kiểm tra database đã xóa
    db_vocab = session.get(Vocabulary, vocab_id)
    assert db_vocab is None


def test_get_vocabulary_stats(auth_client: TestClient):
    """Test lấy thống kê từ vựng."""
    response = auth_client.get("/api/v1/vocabulary/stats")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_vocabularies" in data
    assert "by_difficulty" in data
