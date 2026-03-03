from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ZoneTypeEnum(str, Enum):
    GAMING = "gaming"
    TRAINING = "training"
    TEAM_ROOM = "team_room"


class ZoneCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    zone_type: ZoneTypeEnum
    capacity: int = Field(default=1, ge=1)
    equipment: Optional[str] = None
    price_per_hour: int = Field(default=0, ge=0)
    is_active: bool = True


class ZoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    zone_type: Optional[ZoneTypeEnum] = None
    capacity: Optional[int] = Field(None, ge=1)
    equipment: Optional[str] = None
    price_per_hour: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ZoneResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    zone_type: ZoneTypeEnum
    capacity: int
    equipment: Optional[str]
    price_per_hour: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
