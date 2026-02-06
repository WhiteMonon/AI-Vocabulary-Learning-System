"""Tests cho AI Practice và Quiz Session Integration."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from fastapi.testclient import TestClient

from app.ai.schemas import AIQuestion
from app.models.enums import PracticeType


@pytest.mark.asyncio
async def test_generate_quiz_session_with_mock_ai(auth_client: TestClient, session):
    """Test tạo phiền quiz với AI provider được mock."""
    # 1. Chuẩn bị data: Từ vựng DUE (next_review_date <= now)
    # create_vocabulary endpoint mặc định đặt next_review_date = now (DUE)
    auth_client.post("/api/v1/vocabulary/", json={
        "word": "AI", 
        "meanings": [{"definition": "Artificial Intelligence"}]
    })
    
    # 2. Mock AI Provider
    mock_ai_question = AIQuestion(
        question_text="What does AI stand for?",
        options={"A": "Apple", "B": "Artificial Intelligence", "C": "Action"},
        correct_answer="B",
        explanation="AI is the simulation of human intelligence.",
        practice_type=PracticeType.MULTIPLE_CHOICE
    )
    
    with patch("app.services.vocabulary_service.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_question.return_value = mock_ai_question
        mock_get_provider.return_value = mock_provider
        
        # 3. Gọi endpoint
        response = auth_client.get("/api/v1/vocabulary/quiz-session?limit=5")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) > 0
        assert data["questions"][0]["word"] == "ai"
        assert data["questions"][0]["question_text"] == "What does AI stand for?"


def test_generate_quiz_session_no_due_words(auth_client: TestClient, session):
    """Test không tạo session nếu không có từ vựng đến hạn."""
    # Xử lý: Mặc dù create_vocab mặc định là DUE, trong thực tế ta có thể 
    # update next_review_date vào tương lai để test case này.
    # Nhưng đơn giản nhất là test với user mới tinh chưa có từ vựng nào.
    
    response = auth_client.get("/api/v1/vocabulary/quiz-session")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["questions"] == []
