"""Tests cho các tính năng quản lý từ vựng mới: Import/Export, Word Classification."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from unittest.mock import AsyncMock, patch

from app.models.vocabulary import Vocabulary
from app.models.enums import WordType, MeaningSource


def test_word_classification_logic(auth_client: TestClient, session: Session):
    """Test từ vựng được phân loại đúng (Function vs Content)."""
    # 1. Test Content Word
    res1 = auth_client.post("/api/v1/vocabulary/", json={
        "word": "Stunning", 
        "meanings": [{"definition": "Very beautiful"}]
    })
    assert res1.json()["word_type"] == "content_word"
    assert res1.json()["is_word_type_manual"] is False
    
    # 2. Test Function Word
    res2 = auth_client.post("/api/v1/vocabulary/", json={
        "word": "Although", 
        "meanings": [{"definition": "In spite of the fact that"}]
    })
    assert res2.json()["word_type"] == "function_word"
    
    # 3. Test Manual Override
    res3 = auth_client.post("/api/v1/vocabulary/", json={
        "word": "In", 
        "meanings": [{"definition": "Inside"}],
        "word_type": "content_word"
    })
    assert res3.json()["word_type"] == "content_word"
    assert res3.json()["is_word_type_manual"] is True


@pytest.mark.asyncio
async def test_import_from_txt_basic(auth_client: TestClient, session: Session):
    """Test import cơ bản từ file TXT."""
    content = "apple|quả táo|I eat an apple\nbanana|quả chuối"
    
    # Mock DictionaryService để không gọi API thật
    with patch("app.services.vocabulary_service.DictionaryService") as mock_service_class:
        response = auth_client.post("/api/v1/vocabulary/import", json={
            "content": content,
            "auto_fetch_meaning": False
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_processed"] == 2
        assert data["new_words"] == 2
        
        # Kiểm tra DB
        stmt = select(Vocabulary).where(Vocabulary.word == "apple").options(selectinload(Vocabulary.meanings))
        vocab = session.exec(stmt).first()
        assert vocab is not None
        assert vocab.meanings[0].definition == "quả táo"
        assert vocab.meanings[0].example_sentence == "I eat an apple"


@pytest.mark.asyncio
async def test_import_with_auto_meaning(auth_client: TestClient, session: Session):
    """Test import có tự động fetch nghĩa khi thiếu."""
    content = "strawberry"
    
    with patch("app.services.dictionary_service.DictionaryService.batch_get_definitions") as mock_batch:
        mock_batch.return_value = {
            "strawberry": ("A red fruit", MeaningSource.DICTIONARY_API)
        }
        
        response = auth_client.post("/api/v1/vocabulary/import", json={
            "content": content,
            "auto_fetch_meaning": True
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["auto_generated_count"] == 1
        
        # Kiểm tra DB
        stmt = select(Vocabulary).where(Vocabulary.word == "strawberry").options(selectinload(Vocabulary.meanings))
        vocab = session.exec(stmt).first()
        assert vocab.meanings[0].definition == "A red fruit"
        assert vocab.meanings[0].meaning_source == "dictionary_api"


def test_export_vocabularies_json(auth_client: TestClient):
    """Test export danh sách từ vựng sang JSON."""
    # Tạo data
    auth_client.post("/api/v1/vocabulary/", json={
        "word": "export1", 
        "meanings": [{"definition": "def1"}]
    })
    
    response = auth_client.get("/api/v1/vocabulary/export?format=json")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert any(item["word"] == "export1" for item in data)


def test_export_vocabularies_txt(auth_client: TestClient):
    """Test export sang format TXT."""
    auth_client.post("/api/v1/vocabulary/", json={
        "word": "export2", 
        "meanings": [{"definition": "def2", "example_sentence": "ex2"}]
    })
    
    response = auth_client.get("/api/v1/vocabulary/export?format=txt")
    assert response.status_code == status.HTTP_200_OK
    assert "export2|def2|ex2" in response.text
