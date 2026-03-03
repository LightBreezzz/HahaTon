from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class BookingStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class BookingCreate(BaseModel):
    zone_id: int = Field(..., gt=0)
    start_time: datetime
    end_time: datetime
    comment: Optional[str] = None
    
    @field_validator('end_time')
    @classmethod
    def end_must_be_after_start(cls, v, info):
        # Валидация будет дополнена в сервисе
        return v


class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatusEnum] = None
    comment: Optional[str] = None
    admin_comment: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    user_id: int
    zone_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatusEnum
    comment: Optional[str]
    admin_comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Дополнительные поля для отображения
    zone_name: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class BookingConflict(BaseModel):
    """Информация о конфликте бронирований"""
    has_conflict: bool
    conflicting_bookings: list[int] = []
    message: Optional[str] = None
