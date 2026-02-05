"""
API v1 router.
Tổng hợp tất cả endpoints cho API version 1.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health_router
from app.api.v1.endpoints.vocabulary import router as vocabulary_router

# Tạo main router cho API v1
api_router = APIRouter()

# Include các endpoint routers
api_router.include_router(health_router, tags=["Health"])

# Vocabulary endpoints
api_router.include_router(
    vocabulary_router, 
    prefix="/vocabulary", 
    tags=["Vocabulary"]
)
