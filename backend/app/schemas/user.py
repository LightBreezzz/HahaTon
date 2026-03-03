from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Пароль минимум 6 символов")
    full_name: str = Field(..., min_length=2, description="Имя пользователя")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
