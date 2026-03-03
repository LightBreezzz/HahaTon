from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.booking import Booking, BookingStatus
from ..models.zone import Zone
from ..models.user import User
from ..schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from ..routers.dependencies import get_current_active_user, get_current_admin_user
from ..services.booking_service import booking_service

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Создание нового бронирования"""
    
    # Проверяем существование зоны
    result = await db.execute(select(Zone).where(Zone.id == booking_data.zone_id))
    zone = result.scalar_one_or_none()
    
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зона не найдена"
        )
    
    if not zone.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Эта зона временно недоступна"
        )
    
    # Проверка: end_time > start_time
    if booking_data.end_time <= booking_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время окончания должно быть позже времени начала"
        )
    
    # Проверка на пересечение с другими бронированиями этой зоны
    has_conflict, conflicting_ids = await booking_service.check_time_conflict(
        db,
        zone_id=booking_data.zone_id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time
    )
    
    if has_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Время уже забронировано. Конфликтующие бронирования: {conflicting_ids}"
        )
    
    # Проверка: не забронировал ли пользователь уже что-то на это время
    has_user_conflict, _ = await booking_service.check_user_conflict(
        db,
        user_id=current_user.id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time
    )
    
    if has_user_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="У вас уже есть бронирование на это время"
        )
    
    # Создаем бронирование
    new_booking = Booking(
        user_id=current_user.id,
        zone_id=booking_data.zone_id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        comment=booking_data.comment,
        status=BookingStatus.CONFIRMED  # Автоматически подтверждаем
    )
    
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    
    # Формируем ответ
    return {
        "id": new_booking.id,
        "user_id": new_booking.user_id,
        "zone_id": new_booking.zone_id,
        "start_time": new_booking.start_time,
        "end_time": new_booking.end_time,
        "status": new_booking.status.value,
        "comment": new_booking.comment,
        "admin_comment": new_booking.admin_comment,
        "created_at": new_booking.created_at,
        "updated_at": new_booking.updated_at,
        "zone_name": zone.name,
        "user_name": current_user.full_name
    }


@router.get("", response_model=List[BookingResponse])
async def get_all_bookings(
    status_filter: Optional[BookingStatus] = Query(None, alias="status"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех бронирований (только админ)"""
    
    query = select(Booking).order_by(Booking.start_time.desc())
    
    if status_filter:
        query = query.where(Booking.status == status_filter)
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    # Формируем ответ с именами
    booking_list = []
    for booking in bookings:
        user_result = await db.execute(
            select(User.full_name).where(User.id == booking.user_id)
        )
        zone_result = await db.execute(
            select(Zone.name).where(Zone.id == booking.zone_id)
        )
        user_name = user_result.scalar_one_or_none()
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
            "user_name": user_name
        })
    
    return booking_list


@router.get("/my", response_model=List[BookingResponse])
async def get_my_bookings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение моих бронирований"""
    
    bookings = await booking_service.get_bookings_for_user(db, current_user.id)
    
    booking_list = []
    for booking in bookings:
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
            "user_name": current_user.full_name
        })
    
    return booking_list


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о бронировании"""
    
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    # Проверка доступа: только владелец или админ
    if booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому бронированию"
        )
    
    zone_result = await db.execute(
        select(Zone.name).where(Zone.id == booking.zone_id)
    )
    zone_name = zone_result.scalar_one_or_none()
    
    return {
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
        "user_name": current_user.full_name
    }


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление бронирования"""
    
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    # Проверка доступа
    is_admin = current_user.role.value == "admin"
    if booking.user_id != current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому бронированию"
        )
    
    update_data = booking_data.model_dump(exclude_unset=True)
    
    # Если меняем время - проверяем конфликты
    if "start_time" in update_data or "end_time" in update_data:
        new_start = update_data.get("start_time", booking.start_time)
        new_end = update_data.get("end_time", booking.end_time)
        
        if new_end <= new_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Время окончания должно быть позже времени начала"
            )
        
        has_conflict, _ = await booking_service.check_time_conflict(
            db,
            zone_id=booking.zone_id,
            start_time=new_start,
            end_time=new_end,
            exclude_booking_id=booking_id
        )
        
        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Новое время пересекается с другими бронированиями"
            )
    
    # Только админ может менять статус
    if "status" in update_data and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может менять статус"
        )
    
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    await db.commit()
    await db.refresh(booking)
    
    zone_result = await db.execute(
        select(Zone.name).where(Zone.id == booking.zone_id)
    )
    zone_name = zone_result.scalar_one_or_none()
    
    return {
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
        "user_name": current_user.full_name
    }


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Отмена бронирования"""
    
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    # Проверка доступа
    if booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому бронированию"
        )
    
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Бронирование уже отменено"
        )
    
    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)
    
    zone_result = await db.execute(
        select(Zone.name).where(Zone.id == booking.zone_id)
    )
    zone_name = zone_result.scalar_one_or_none()
    
    return {
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
        "user_name": current_user.full_name
    }
