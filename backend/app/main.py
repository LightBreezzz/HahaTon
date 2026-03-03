from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from .database import init_db, engine, Base
from .config import settings
from .routers import auth_router, users_router, zones_router, bookings_router, admin_router, achievements_router
from .models.user import User, Role
from .models.zone import Zone, ZoneType
from .models.achievement import Achievement
from .utils.security import get_password_hash


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при запуске"""
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем админа по умолчанию
    await create_default_admin()
    
    # Создаем тестовые зоны и достижения
    await create_initial_data()
    
    yield


async def create_default_admin():
    """Создание администратора по умолчанию"""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    from .database import async_session_maker
    
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="Администратор",
                role=Role.ADMIN,
                is_active=True
            )
            db.add(admin)
            await db.commit()
            print(f"[OK] Создан администратор: {settings.ADMIN_EMAIL}")


async def create_initial_data():
    """Создание начальных данных"""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    from .database import async_session_maker
    
    async with async_session_maker() as db:
        # Проверяем, есть ли зоны
        result = await db.execute(select(Zone))
        zones = result.scalars().all()
        
        if not zones:
            # Создаем тестовые зоны
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
            print("[OK] Созданы тестовые зоны")
        
        # Проверяем, есть ли достижения
        result = await db.execute(select(Achievement))
        achievements = result.scalars().all()
        
        if not achievements:
            achievements_data = [
                Achievement(
                    name="Первый шаг",
                    description="Сделайте первое бронирование",
                    icon="🎮",
                    points=5,
                    criterion_type="total_bookings",
                    criterion_value=1
                ),
                Achievement(
                    name="Любитель",
                    description="10 бронирований",
                    icon="🏅",
                    points=20,
                    criterion_type="total_bookings",
                    criterion_value=10
                ),
                Achievement(
                    name="Профи",
                    description="50 бронирований",
                    icon="🏆",
                    points=50,
                    criterion_type="total_bookings",
                    criterion_value=50
                ),
                Achievement(
                    name="Часовой",
                    description="10 часов в игре",
                    icon="⏱️",
                    points=15,
                    criterion_type="total_hours",
                    criterion_value=10
                ),
                Achievement(
                    name="Марафонец",
                    icon="🔥",
                    description="100 часов в игре",
                    points=100,
                    criterion_type="total_hours",
                    criterion_value=100
                ),
            ]
            
            for achievement in achievements_data:
                db.add(achievement)
            
            await db.commit()
            print("[OK] Созданы достижения")


# Создаем приложение
app = FastAPI(
    title="Cyber Arena API",
    description="API для системы бронирования кибер-арены",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для хакатона можно, в продакшене ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(zones_router, prefix="/api")
app.include_router(bookings_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(achievements_router, prefix="/api")


# Монтируем статику и настраиваем пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

@app.get("/")
async def root():
    """Корневая страница - редирект на фронтенд"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)


@app.get("/calendar.html")
async def calendar():
    """Календарь занятости"""
    return FileResponse(os.path.join(FRONTEND_DIR, "calendar.html"))


@app.get("/profile.html")
async def profile():
    """Профиль пользователя"""
    return FileResponse(os.path.join(FRONTEND_DIR, "profile.html"))


@app.get("/admin.html")
async def admin():
    """Админ-панель"""
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "message": "Cyber Arena API работает"}


# Монтируем статику
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
