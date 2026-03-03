from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class BookingStatus(enum.Enum):
    """Статусы бронирования"""
    PENDING = "pending"       # Ожидает подтверждения
    CONFIRMED = "confirmed"   # Подтверждено
    COMPLETED = "completed"   # Завершено
    CANCELLED = "cancelled"   # Отменено
    NO_SHOW = "no_show"       # Клиент не пришел


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)
    
    # Временные слоты
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Информация
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    comment = Column(Text, nullable=True)  # Комментарий пользователя
    admin_comment = Column(Text, nullable=True)  # Комментарий администратора
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Проверка: end_time > start_time
    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_end_time_after_start'),
    )
    
    # Связи
    user = relationship("User", back_populates="bookings")
    zone = relationship("Zone", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, user_id={self.user_id}, zone_id={self.zone_id}, start={self.start_time})>"
