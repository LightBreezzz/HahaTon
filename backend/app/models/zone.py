from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class ZoneType(enum.Enum):
    """Типы зон кибер-арены"""
    GAMING = "gaming"           # Игровая зона (основные ПК)
    TRAINING = "training"       # Тренировочная зона
    TEAM_ROOM = "team_room"     # Командная комната


class Zone(Base):
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    zone_type = Column(SQLEnum(ZoneType), nullable=False)
    capacity = Column(Integer, default=1, nullable=False)  # Количество мест
    equipment = Column(String(500), nullable=True)  # Описание оборудования
    price_per_hour = Column(Integer, default=0, nullable=False)  # Цена в рублях
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    bookings = relationship("Booking", back_populates="zone", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Zone(id={self.id}, name={self.name}, type={self.zone_type.value})>"
