from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Optional
from ..models.booking import Booking, BookingStatus
from ..models.zone import Zone


class BookingService:
    """Сервис для работы с бронированиями"""
    
    @staticmethod
    async def check_time_conflict(
        db: AsyncSession,
        zone_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: Optional[int] = None
    ) -> tuple[bool, List[int]]:
        """
        Проверка пересечения временных слотов для одной зоны.
        
        Логика: два бронирования пересекаются, если:
        - start1 < end2 И end1 > start2
        
        Возвращает: (has_conflict, list_of_conflicting_booking_ids)
        """
        # Строим запрос: ищем все активные бронирования этой зоны,
        # которые пересекаются с указанным временем
        query = select(Booking.id).where(
            and_(
                Booking.zone_id == zone_id,
                Booking.status.notin_([BookingStatus.CANCELLED, BookingStatus.NO_SHOW]),
                # Условие пересечения: start < new_end AND end > new_start
                Booking.start_time < end_time,
                Booking.end_time > start_time,
            )
        )
        
        # Если исключаем текущее бронирование (для обновления)
        if exclude_booking_id:
            query = query.where(Booking.id != exclude_booking_id)
        
        result = await db.execute(query)
        conflicting_ids = [row[0] for row in result.all()]
        
        has_conflict = len(conflicting_ids) > 0
        return has_conflict, conflicting_ids
    
    @staticmethod
    async def check_user_conflict(
        db: AsyncSession,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: Optional[int] = None
    ) -> tuple[bool, List[int]]:
        """
        Проверка: не забронировал ли пользователь уже что-то на это время.
        
        Возвращает: (has_conflict, list_of_conflicting_booking_ids)
        """
        query = select(Booking.id).where(
            and_(
                Booking.user_id == user_id,
                Booking.status.notin_([BookingStatus.CANCELLED, BookingStatus.NO_SHOW]),
                Booking.start_time < end_time,
                Booking.end_time > start_time,
            )
        )
        
        if exclude_booking_id:
            query = query.where(Booking.id != exclude_booking_id)
        
        result = await db.execute(query)
        conflicting_ids = [row[0] for row in result.all()]
        
        has_conflict = len(conflicting_ids) > 0
        return has_conflict, conflicting_ids
    
    @staticmethod
    async def get_bookings_for_zone(
        db: AsyncSession,
        zone_id: int,
        date_from: datetime,
        date_to: datetime
    ) -> List[Booking]:
        """Получить все бронирования зоны за период"""
        query = select(Booking).where(
            and_(
                Booking.zone_id == zone_id,
                Booking.status.notin_([BookingStatus.CANCELLED, BookingStatus.NO_SHOW]),
                or_(
                    # Бронирования, которые начинаются в периоде
                    and_(Booking.start_time >= date_from, Booking.start_time <= date_to),
                    # Бронирования, которые заканчиваются в периоде
                    and_(Booking.end_time >= date_from, Booking.end_time <= date_to),
                    # Бронирования, которые охватывают весь период
                    and_(Booking.start_time <= date_from, Booking.end_time >= date_to),
                )
            )
        )
        result = await db.execute(query)
        return [row[0] for row in result.all()]
    
    @staticmethod
    async def get_bookings_for_user(
        db: AsyncSession,
        user_id: int,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """Получить все бронирования пользователя"""
        query = select(Booking).where(Booking.user_id == user_id)
        
        if status:
            query = query.where(Booking.status == status)
        else:
            # Исключаем отмененные по умолчанию
            query = query.where(Booking.status.notin_([BookingStatus.CANCELLED, BookingStatus.NO_SHOW]))
        
        query = query.order_by(Booking.start_time.desc())
        result = await db.execute(query)
        return [row[0] for row in result.all()]


booking_service = BookingService()
