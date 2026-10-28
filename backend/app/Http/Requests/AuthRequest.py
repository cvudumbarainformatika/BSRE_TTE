from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class RegisterUserRequest(BaseModel):
    username: str
    password: str
    nama: str
    nip: Optional[str] = None
    nik: Optional[str] = None
    email: Optional[str] = None
    role: str = "perawat" # dokter, perawat, ppa, admin
