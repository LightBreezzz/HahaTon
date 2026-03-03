"""
Скрипт для инициализации базы данных и создания тестовых данных
Запуск: python init_db.py
"""

import asyncio
import sys
from pathlib import Path

# Добавляем backend в path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Импортируем модели
from backend.app.models.user import User, Role
from backend.app.models.zone import Zone, ZoneType
from backend.app.models.booking import Booking, BookingStatus
from backend.app.models.achievement import Achievement, UserAchievement
from backend.app.database import Base
from backend.app.utils.security import get_password_hash
from backend.app.config import settings


async def init_db():
    """Инициализация БД и создание тестовых данных"""
    
    # Создаем движок
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    # Создаем таблицы
    print("📦 Создание таблиц...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем сессию
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as db:
        # Создаем админа
        result = await db.execute(select(User).where(User.email == "admin@hahaton.ru"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("👤 Создание администратора...")
            admin = User(
                email="admin@hahaton.ru",
                hashed_password=get_password_hash("admin123"),
                full_name="Администратор",
                role=Role.ADMIN,
                is_active=True
            )
            db.add(admin)
            await db.commit()
            print("✅ Администратор создан: admin@hahaton.ru / admin123")
        else:
            print("✅ Администратор уже существует")
        
        # Создаем тестовые зоны
        result = await db.execute(select(Zone))
        zones = result.scalars().all()
        
        if not zones:
            print("🎮 Создание тестовых зон...")
            zones_data = [
                Zone(name="PC-1", description="Игровой ПК #1 - RTX 3060, 144Hz", 
                     zone_type=ZoneType.GAMING, capacity=1, equipment="RTX 3060, i5-12400F, 16GB RAM", price_per_hour=100),
                Zone(name="PC-2", description="Игровой ПК #2 - RTX 3070, 165Hz", 
                     zone_type=ZoneType.GAMING, capacity=1, equipment="RTX 3070, i5-13400F, 16GB RAM", price_per_hour=150),
                Zone(name="PC-3", description="Игровой ПК #3 - RTX 4060, 240Hz", 
                     zone_type=ZoneType.GAMING, capacity=1, equipment="RTX 4060, i7-13700F, 32GB RAM", price_per_hour=200),
                Zone(name="Training-1", description="Тренировочная зона #1", 
                     zone_type=ZoneType.TRAINING, capacity=2, equipment="RTX 2060, i3-12100F, 8GB RAM", price_per_hour=50),
                Zone(name="Team Room Alpha", description="Командная комната на 5 человек", 
                     zone_type=ZoneType.TEAM_ROOM, capacity=5, equipment="5x ПК RTX 3060, проектор, звук", price_per_hour=500),
            ]
            
            for zone in zones_data:
                db.add(zone)
            
            await db.commit()
            print(f"✅ Создано {len(zones_data)} зон")
        else:
            print(f"✅ Зоны уже существуют ({len(zones)} шт.)")
        
        # Создаем достижения
        result = await db.execute(select(Achievement))
        achievements = result.scalars().all()
        
        if not achievements:
            print("🏆 Создание достижений...")
            achievements_data = [
                Achievement(name="Первый шаг", description="Сделайте первое бронирование", icon="🎮", points=5, criterion_type="total_bookings", criterion_value=1),
                Achievement(name="Любитель", description="10 бронирований", icon="🏅", points=20, criterion_type="total_bookings", criterion_value=10),
                Achievement(name="Профи", description="50 бронирований", icon="🏆", points=50, criterion_type="total_bookings", criterion_value=50),
                Achievement(name="Часовой", description="10 часов в игре", icon="⏱️", points=15, criterion_type="total_hours", criterion_value=10),
                Achievement(name="Марафонец", description="100 часов в игре", icon="🔥", points=100, criterion_type="total_hours", criterion_value=100),
            ]
            
            for achievement in achievements_data:
                db.add(achievement)
            
            await db.commit()
            print(f"✅ Создано {len(achievements_data)} достижений")
        else:
            print(f"✅ Достижения уже существуют ({len(achievements)} шт.)")
        
        # Создаем тестового пользователя
        result = await db.execute(select(User).where(User.email == "user@test.ru"))
        test_user = result.scalar_one_or_none()
        
        if not test_user:
            print("👤 Создание тестового пользователя...")
            test_user = User(
                email="user@test.ru",
                hashed_password=get_password_hash("user123"),
                full_name="Тестовый пользователь",
                role=Role.USER,
                is_active=True
            )
            db.add(test_user)
            await db.commit()
            print("✅ Тестовый пользователь создан: user@test.ru / user123")
        else:
            print("✅ Тестовый пользователь уже существует")
    
    await engine.dispose()
    
    print("\n" + "=" * 50)
    print("✅ Инициализация завершена!")
    print("=" * 50)
    print("\nТестовые учетные данные:")
    print("  Админ: admin@hahaton.ru / admin123")
    print("  Пользователь: user@test.ru / user123")
    print("\nЗапустите сервер: uvicorn backend.app.main:app --reload")
    print("Документация API: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(init_db())
