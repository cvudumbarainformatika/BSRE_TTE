from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class SsoLoginRequest(BaseModel):
    sso_token: Optional[str] = None
    nip: Optional[str] = None
    username: Optional[str] = None
    auth_key: Optional[str] = None

class LoginQrSimrsRequest(BaseModel):
    email: str
    token: Optional[str] = None

class QrGenerateCustomRequest(BaseModel):
    custom_code: Optional[str] = None


class QrGenerateResponse(BaseModel):
    session_id: str
    qr_payload: str
    qr_image_base64: str
    expires_in_seconds: int

class QrStatusResponse(BaseModel):
    session_id: str
    status: str # PENDING, SCANNED, APPROVED, EXPIRED
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[dict] = None

class QrApproveRequest(BaseModel):
    session_id: str
    nip: str
    auth_key: Optional[str] = None

class RegisterUserRequest(BaseModel):
    username: str
    password: str
    nama: str
    nip: Optional[str] = None
    nik: Optional[str] = None
    email: Optional[str] = None
    role: str = "perawat" # dokter, perawat, ppa, admin
