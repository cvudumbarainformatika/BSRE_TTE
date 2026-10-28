from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from config.database import get_session
from app.Models.User import User, UserRole
from app.Http.Requests.AuthRequest import LoginRequest, TokenResponse, RegisterUserRequest
from app.Http.Middleware.AuthMiddleware import (
    verify_password, get_password_hash, create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == req.username)).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun pengguna tidak aktif"
        )

    role_val = user.role.value if hasattr(user.role, 'value') else str(user.role)
    token = create_access_token({
        "sub": user.username,
        "role": role_val,
        "id": user.id,
        "nama": user.nama,
        "nip": user.nip
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "nama": user.nama,
            "role": role_val,
            "nip": user.nip,
            "email": user.email
        }
    }

@router.post("/register")
def register(req: RegisterUserRequest, db: Session = Depends(get_session)):
    existing = db.exec(select(User).where(User.username == req.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username sudah digunakan")

    user = User(
        username=req.username,
        nama=req.nama,
        nip=req.nip,
        nik=req.nik,
        email=req.email,
        role=UserRole(req.role.lower()),
        hashed_password=get_password_hash(req.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User berhasil didaftarkan", "id": user.id, "username": user.username}

@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "nama": current_user.nama,
        "nip": current_user.nip,
        "role": role_val,
        "email": current_user.email
    }
