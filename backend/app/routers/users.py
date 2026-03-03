from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.booking import Booking, BookingStatus
from ..schemas.user import UserResponse, UserUpdate
from ..schemas.booking import BookingResponse
from ..routers.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Получение профиля текущего пользователя"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление профиля текущего пользователя"""
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/me/bookings", response_model=List[BookingResponse])
async def get_my_bookings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех бронирований текущего пользователя"""
    
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.start_time.desc())
    )
    bookings = result.scalars().all()
    
    # Добавляем имена зон
    booking_list = []
    for booking in bookings:
        zone_result = await db.execute(
            select(Booking.zone).where(Booking.id == booking.id)
        )
        zone = zone_result.scalar_one_or_none()
        
        booking_dict = {
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
            "zone_name": zone.name if zone else None,
            "user_name": current_user.full_name
        }
        booking_list.append(booking_dict)
    
    return booking_list
