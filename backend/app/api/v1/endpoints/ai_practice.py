from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.api import deps
from app.ai.factory import get_ai_provider
from app.ai.schemas import AIChatRequest
from app.models.user import User

router = APIRouter()

@router.post("/chat")
async def chat_with_ai(
    request: AIChatRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Endpoint cho phép người dùng chat với AI để luyện tập từ vựng.
    Trả về StreamingResponse để hiển thị kết quả dần dần.
    """
    try:
        provider = get_ai_provider()
        
        async def event_generator():
            async for chunk in provider.chat_stream(request.messages):
                yield chunk

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
