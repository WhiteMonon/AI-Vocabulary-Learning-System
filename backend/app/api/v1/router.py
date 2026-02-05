"""
API v1 router.
Tổng hợp tất cả endpoints cho API version 1.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health_router
from app.api.v1.endpoints.vocabulary import router as vocabulary_router
from app.api.v1.endpoints.auth import router as auth_router

# Tạo main router cho API v1
api_router = APIRouter()

# Include các endpoint routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Vocabulary endpoints
api_router.include_router(
    vocabulary_router, 
    prefix="/vocabulary", 
    tags=["Vocabulary"]
)
