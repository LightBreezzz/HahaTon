from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    points: int
    criterion_type: str
    criterion_value: int
    is_active: bool
    
    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    id: int
    user_id: int
    achievement_id: int
    earned_at: datetime
    
    achievement: Optional[AchievementResponse] = None
    
    class Config:
        from_attributes = True
