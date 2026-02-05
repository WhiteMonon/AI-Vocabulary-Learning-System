"""
SQLModel base classes và common fields.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin class cung cấp timestamp fields cho tất cả models."""
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Thời điểm tạo record"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Thời điểm cập nhật record cuối cùng"
    )


class BaseModel(TimestampMixin):
    """
    Base model class cho tất cả database models.
    Cung cấp id và timestamp fields.
    """
    
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Primary key"
    )
