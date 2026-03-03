from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.achievement import Achievement, UserAchievement
from ..schemas.achievement import AchievementResponse, UserAchievementResponse
from ..routers.dependencies import get_current_active_user

router = APIRouter(prefix="/achievements", tags=["Достижения"])


@router.get("", response_model=List[AchievementResponse])
async def get_all_achievements(
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех достижений"""
    
    result = await db.execute(
        select(Achievement).where(Achievement.is_active == True)
    )
    achievements = result.scalars().all()
    
    return achievements


@router.get("/my", response_model=List[UserAchievementResponse])
async def get_my_achievements(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение моих достижений"""
    
    result = await db.execute(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
        .order_by(UserAchievement.earned_at.desc())
    )
    user_achievements = result.scalars().all()
    
    # Формируем ответ с деталями достижений
    response_list = []
    for ua in user_achievements:
        achievement_result = await db.execute(
            select(Achievement).where(Achievement.id == ua.achievement_id)
        )
        achievement = achievement_result.scalar_one_or_none()
        
        response_list.append({
            "id": ua.id,
            "user_id": ua.user_id,
            "achievement_id": ua.achievement_id,
            "earned_at": ua.earned_at,
            "achievement": {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "points": achievement.points,
                "criterion_type": achievement.criterion_type,
                "criterion_value": achievement.criterion_value,
                "is_active": achievement.is_active
            } if achievement else None
        })
    
    return response_list
