from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum

class UserRole(str, Enum):
    DOKTER = "dokter"
    PERAWAT = "perawat"
    PPA = "ppa"
    ADMIN = "admin"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    nama: str = Field(max_length=255)
    nip: Optional[str] = Field(default=None, max_length=50, index=True)
    nik: Optional[str] = Field(default=None, max_length=20, index=True)
    email: Optional[str] = Field(default=None, max_length=100)
    role: UserRole = Field(default=UserRole.PERAWAT, index=True)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
