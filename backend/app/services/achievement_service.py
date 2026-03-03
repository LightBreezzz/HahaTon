from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
from ..models.achievement import Achievement, UserAchievement
from ..models.booking import Booking, BookingStatus
from ..models.user import User


class AchievementService:
    """Сервис для работы с достижениями"""
    
    @staticmethod
    async def check_and_award(db: AsyncSession, user_id: int) -> List[Achievement]:
        """
        Проверить и выдать достижения пользователю.
        Вызывается после завершения бронирования.
        """
        awarded = []
        
        # Получаем все достижения пользователя
        result = await db.execute(
            select(UserAchievement.achievement_id).where(
                UserAchievement.user_id == user_id
            )
        )
        earned_ids = {row[0] for row in result.all()}
        
        # Получаем статистику пользователя
        total_bookings = await db.execute(
            select(func.count()).where(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.COMPLETED
            )
        )
        total_bookings = total_bookings.scalar()
        
        total_hours_result = await db.execute(
            select(func.sum(Booking.end_time - Booking.start_time)).where(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.COMPLETED
            )
        )
        total_hours = total_hours_result.scalar() or 0
        total_hours = total_hours.total_seconds() / 3600  # Конвертируем в часы
        
        # Получаем все активные достижения
        result = await db.execute(
            select(Achievement).where(Achievement.is_active == True)
        )
        all_achievements = result.scalars().all()
        
        # Проверяем каждое достижение
        for achievement in all_achievements:
            if achievement.id in earned_ids:
                continue  # Уже получено
            
            should_award = False
            
            if achievement.criterion_type == "total_bookings":
                should_award = total_bookings >= achievement.criterion_value
            elif achievement.criterion_type == "total_hours":
                should_award = total_hours >= achievement.criterion_value
            
            if should_award:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.add(user_achievement)
                awarded.append(achievement)
        
        await db.commit()
        return awarded
    
    @staticmethod
    async def get_user_achievements(db: AsyncSession, user_id: int) -> List[UserAchievement]:
        """Получить все достижения пользователя"""
        result = await db.execute(
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.earned_at.desc())
        )
        return result.scalars().all()


achievement_service = AchievementService()
