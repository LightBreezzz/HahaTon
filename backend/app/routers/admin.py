from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User, Role
from ..models.zone import Zone
from ..models.booking import Booking, BookingStatus
from ..schemas.user import UserResponse
from ..schemas.zone import ZoneResponse
from ..schemas.booking import BookingResponse
from ..routers.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Админ-панель"])


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики для админ-панели"""
    
    # Всего пользователей
    users_count = await db.execute(select(func.count(User.id)))
    users_count = users_count.scalar()
    
    # Всего зон
    zones_count = await db.execute(select(func.count(Zone.id)).where(Zone.is_active == True))
    zones_count = zones_count.scalar()
    
    # Бронирования по статусам
    bookings_by_status = {}
    for status in BookingStatus:
        count = await db.execute(
            select(func.count(Booking.id)).where(Booking.status == status)
        )
        bookings_by_status[status.value] = count.scalar()
    
    # Бронирования сегодня
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    today_bookings = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.start_time >= today_start,
            Booking.start_time < today_end
        )
    )
    today_bookings = today_bookings.scalar()
    
    # Выручка за сегодня (сумма часов * цена)
    today_revenue_result = await db.execute(
        select(func.sum(Zone.price_per_hour * 
            func.extract('epoch', Booking.end_time - Booking.start_time) / 3600
        )).where(
            Booking.status == BookingStatus.COMPLETED,
            Booking.start_time >= today_start,
            Booking.start_time < today_end
        ).join(Zone, Booking.zone_id == Zone.id)
    )
    today_revenue = today_revenue_result.scalar() or 0
    
    return {
        "total_users": users_count,
        "total_zones": zones_count,
        "bookings_by_status": bookings_by_status,
        "today_bookings": today_bookings,
        "today_revenue": round(today_revenue, 2)
    }


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех пользователей (админ)"""
    
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    
    return users


@router.get("/bookings", response_model=List[BookingResponse])
async def get_all_bookings_admin(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех бронирований с деталями (админ)"""
    
    result = await db.execute(
        select(Booking).order_by(Booking.start_time.desc())
    )
    bookings = result.scalars().all()
    
    booking_list = []
    for booking in bookings:
        user_result = await db.execute(
            select(User.full_name, User.email).where(User.id == booking.user_id)
        )
        user_data = user_result.one_or_none()
        
        zone_result = await db.execute(
            select(Zone.name).where(Zone.id == booking.zone_id)
        )
        zone_name = zone_result.scalar_one_or_none()
        
        booking_list.append({
            "id": booking.id,
            "user_id": booking.user_id,
            "zone_id": booking.zone_id,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "status": booking.status.value,
            "comment": booking.comment,
            "admin_comment": booking.admin_comment,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
            "zone_name": zone_name,
            "user_name": user_data[0] if user_data else None,
            "user_email": user_data[1] if user_data else None
        })
    
    return booking_list


@router.get("/zones/all", response_model=List[ZoneResponse])
async def get_all_zones_admin(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех зон включая неактивные (админ)"""
    
    result = await db.execute(select(Zone).order_by(Zone.name))
    zones = result.scalars().all()
    
    return zones
