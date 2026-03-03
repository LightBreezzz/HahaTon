from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.zone import Zone, ZoneType
from ..models.booking import Booking, BookingStatus
from ..schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse
from ..schemas.booking import BookingResponse
from ..routers.dependencies import get_current_active_user, get_current_admin_user
from ..models.user import User
from ..services.booking_service import booking_service

router = APIRouter(prefix="/zones", tags=["Зоны"])


@router.get("", response_model=List[ZoneResponse])
async def get_all_zones(
    zone_type: Optional[ZoneType] = Query(None, description="Фильтр по типу зоны"),
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех зон"""
    
    query = select(Zone).where(Zone.is_active == is_active)
    
    if zone_type:
        query = query.where(Zone.zone_type == zone_type)
    
    query = query.order_by(Zone.name)
    result = await db.execute(query)
    zones = result.scalars().all()
    
    return zones


@router.get("/{zone_id}", response_model=ZoneResponse)
async def get_zone(
    zone_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о зоне"""
    
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зона не найдена"
        )
    
    return zone


@router.get("/{zone_id}/schedule")
async def get_zone_schedule(
    zone_id: int,
    date_from: datetime = Query(..., description="Начало периода"),
    date_to: datetime = Query(..., description="Конец периода"),
    db: AsyncSession = Depends(get_db)
):
    """Получение расписания зоны за период"""
    
    # Проверяем существование зоны
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зона не найдена"
        )
    
    # Получаем бронирования
    bookings = await booking_service.get_bookings_for_zone(db, zone_id, date_from, date_to)
    
    # Формируем ответ
    schedule = []
    for booking in bookings:
        user_result = await db.execute(
            select(User.full_name).where(User.id == booking.user_id)
        )
        user_name = user_result.scalar_one_or_none()
        
        schedule.append({
            "id": booking.id,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "status": booking.status.value,
            "user_name": user_name
        })
    
    return {
        "zone_id": zone_id,
        "zone_name": zone.name,
        "date_from": date_from,
        "date_to": date_to,
        "bookings": schedule
    }


@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(
    zone_data: ZoneCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Создание новой зоны (только админ)"""
    
    new_zone = Zone(**zone_data.model_dump())
    db.add(new_zone)
    await db.commit()
    await db.refresh(new_zone)
    
    return new_zone


@router.put("/{zone_id}", response_model=ZoneResponse)
async def update_zone(
    zone_id: int,
    zone_data: ZoneUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление зоны (только админ)"""
    
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зона не найдена"
        )
    
    update_data = zone_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(zone, field, value)
    
    await db.commit()
    await db.refresh(zone)
    
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(
    zone_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Удаление зоны (только админ)"""
    
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зона не найдена"
        )
    
    # Мягкое удаление - помечаем как неактивную
    zone.is_active = False
    await db.commit()
    
    return None
