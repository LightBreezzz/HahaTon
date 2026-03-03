from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Achievement(Base):
    """Справочник достижений"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(255), default="🏆", nullable=False)  # Эмодзи или иконка
    points = Column(Integer, default=10, nullable=False)  # Очки за достижение
    
    # Условия получения (критерии)
    criterion_type = Column(String(100), nullable=False)  # Например: "total_bookings", "total_hours"
    criterion_value = Column(Integer, default=0, nullable=False)  # Значение для получения
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Achievement(id={self.id}, name={self.name})>"


class UserAchievement(Base):
    """Достижения пользователей"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    
    earned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"
